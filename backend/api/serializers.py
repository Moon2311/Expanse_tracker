from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from api.models import (
    ChatMessage,
    Expense,
    GroupExpenseSplit,
    GroupInvitation,
    GroupMembership,
    Notification,
    SpendGroup,
    User,
)
from api.utils.splits import split_amount_equally


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "display_name", "date_joined")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "display_name")

    def validate_email(self, value):
        v = (value or "").strip().lower()
        if User.objects.filter(email__iexact=v).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return v

    def validate_username(self, value):
        u = (value or "").strip().lower()
        if User.objects.filter(username__iexact=u).exists():
            raise serializers.ValidationError("This username is taken.")
        return u

    def validate(self, attrs):
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        pwd = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "display_name", "date_joined")
        read_only_fields = ("id", "username", "email", "date_joined")


class SpendGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = SpendGroup
        fields = ("id", "name", "owner", "created_at", "member_count")
        read_only_fields = ("id", "owner", "created_at", "member_count")

    def get_member_count(self, obj):
        return obj.members.count()


class SpendGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendGroup
        fields = ("name",)

    def create(self, validated_data):
        user = self.context["request"].user
        with transaction.atomic():
            g = SpendGroup.objects.create(owner=user, **validated_data)
            GroupMembership.objects.create(user=user, group=g)
        return g


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = (
            "id",
            "amount",
            "description",
            "category",
            "spent_on",
            "created_by",
            "group",
            "kind",
            "created_at",
        )
        read_only_fields = ("id", "created_by", "created_at")

    def validate(self, attrs):
        kind = attrs.get("kind", getattr(self.instance, "kind", None))
        group = attrs.get("group", getattr(self.instance, "group", None))
        if kind == Expense.Kind.PERSONAL and group is not None:
            raise serializers.ValidationError("Personal expenses cannot have a group.")
        if kind == Expense.Kind.GROUP and group is None:
            raise serializers.ValidationError("Group expenses require a group.")
        return attrs


class PersonalExpenseSerializer(ExpenseSerializer):
    """kind/group are set server-side; clients send amount, dates, description, category only."""

    class Meta(ExpenseSerializer.Meta):
        read_only_fields = ("id", "created_by", "created_at", "kind", "group")

    def create(self, validated_data):
        validated_data["kind"] = Expense.Kind.PERSONAL
        validated_data["group"] = None
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class GroupExpenseSplitSerializer(serializers.ModelSerializer):
    owee_username = serializers.CharField(source="owee.username", read_only=True)
    owee_display_name = serializers.CharField(source="owee.display_name", read_only=True)

    class Meta:
        model = GroupExpenseSplit
        fields = (
            "id",
            "owee",
            "owee_username",
            "owee_display_name",
            "share_amount",
            "status",
            "paid_at",
            "created_at",
        )
        read_only_fields = fields


class GroupExpenseListSerializer(serializers.ModelSerializer):
    split_count = serializers.SerializerMethodField()
    recorded_by_username = serializers.CharField(source="created_by.username", read_only=True)
    recorded_by_id = serializers.UUIDField(source="created_by.id", read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id",
            "amount",
            "description",
            "category",
            "spent_on",
            "created_by",
            "recorded_by_username",
            "recorded_by_id",
            "created_at",
            "split_count",
        )
        read_only_fields = fields

    def get_split_count(self, obj):
        return obj.splits.count()


class GroupExpenseReadSerializer(serializers.ModelSerializer):
    splits = GroupExpenseSplitSerializer(many=True, read_only=True)
    recorded_by_username = serializers.CharField(source="created_by.username", read_only=True)
    recorded_by_display_name = serializers.CharField(
        source="created_by.display_name", read_only=True
    )
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id",
            "amount",
            "description",
            "category",
            "spent_on",
            "created_by",
            "recorded_by_username",
            "recorded_by_display_name",
            "group",
            "group_name",
            "kind",
            "created_at",
            "splits",
        )
        read_only_fields = fields


class GroupExpenseSerializer(ExpenseSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list,
    )

    class Meta(ExpenseSerializer.Meta):
        fields = ExpenseSerializer.Meta.fields + ("participant_ids",)
        read_only_fields = ("id", "created_by", "created_at", "kind", "group")

    def validate(self, attrs):
        attrs = dict(attrs)
        attrs["kind"] = Expense.Kind.GROUP
        attrs["group"] = self.context["group"]
        return super().validate(attrs)

    def validate_participant_ids(self, value):
        group = self.context["group"]
        member_ids = set(group.members.values_list("id", flat=True))
        for uid in value:
            if uid not in member_ids:
                raise serializers.ValidationError(
                    "All selected people must be members of this group."
                )
        return value

    def create(self, validated_data):
        request = self.context["request"]
        group = self.context["group"]
        user = request.user
        if not GroupMembership.objects.filter(group=group, user=user).exists():
            raise serializers.ValidationError("You are not a member of this group.")

        participant_ids = validated_data.pop("participant_ids", [])
        validated_data["kind"] = Expense.Kind.GROUP
        validated_data["group"] = group
        validated_data["created_by"] = user
        amount = validated_data["amount"]

        participants = sorted(set(participant_ids) | {user.id})
        desc = (validated_data.get("description") or "").strip() or "expense"

        with transaction.atomic():
            expense = Expense.objects.create(**validated_data)
            if len(participants) < 2:
                return expense

            shares = split_amount_equally(amount, len(participants))
            share_map = dict(zip(participants, shares))
            owees = [uid for uid in participants if uid != user.id]

            for owee_id in owees:
                share = share_map[owee_id]
                split = GroupExpenseSplit.objects.create(
                    expense=expense,
                    owee_id=owee_id,
                    share_amount=share,
                    status=GroupExpenseSplit.Status.PENDING,
                )
                Notification.objects.create(
                    user_id=owee_id,
                    notification_type="group_split_owed",
                    body=(
                        f"@{user.username} split ₹{share} with you in “{group.name}” "
                        f'for “{desc}”. You owe them your share; mark paid when settled.'
                    ),
                    metadata={
                        "expense_id": str(expense.id),
                        "group_id": str(group.id),
                        "split_id": str(split.id),
                    },
                )
        return expense

    def update(self, instance, validated_data):
        validated_data.pop("participant_ids", None)
        amount_changed = "amount" in validated_data and validated_data["amount"] != instance.amount
        instance = super().update(instance, validated_data)
        if amount_changed and instance.splits.exists():
            recalculate_expense_splits(instance)
        return instance


def recalculate_expense_splits(expense: Expense):
    splits = list(expense.splits.select_related("owee").order_by("created_at"))
    if not splits:
        return
    payer_id = expense.created_by_id
    owee_ids = [s.owee_id for s in splits]
    participants = sorted(set(owee_ids) | {payer_id})
    share_map = dict(
        zip(participants, split_amount_equally(expense.amount, len(participants)))
    )
    for s in splits:
        s.share_amount = share_map[s.owee_id]
        s.save(update_fields=["share_amount"])


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "body",
            "read_at",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "sender",
            "sender_username",
            "group",
            "recipient",
            "body",
            "created_at",
        )
        read_only_fields = ("id", "sender", "sender_username", "created_at")


class CreateInviteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)


class InvitationSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    inviter_username = serializers.CharField(source="inviter.username", read_only=True)

    class Meta:
        model = GroupInvitation
        fields = (
            "id",
            "group",
            "group_name",
            "inviter",
            "inviter_username",
            "invitee",
            "status",
            "created_at",
        )
        read_only_fields = (
            "id",
            "group",
            "group_name",
            "inviter",
            "inviter_username",
            "invitee",
            "status",
            "created_at",
        )
