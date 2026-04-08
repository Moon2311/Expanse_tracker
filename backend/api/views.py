from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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
from api.permissions import (
    IsExpenseOwnerForPersonal,
    IsGroupExpenseEditor,
    IsGroupMember,
    IsMemberOfGroupFromUrl,
)
from api.responses import fail, ok
from api.serializers import (
    ChatMessageSerializer,
    CreateInviteSerializer,
    ExpenseSerializer,
    GroupExpenseListSerializer,
    GroupExpenseReadSerializer,
    GroupExpenseSerializer,
    GroupExpenseSplitSerializer,
    InvitationSerializer,
    NotificationSerializer,
    PersonalExpenseSerializer,
    ProfileSerializer,
    RegisterSerializer,
    SpendGroupCreateSerializer,
    SpendGroupSerializer,
    UserPublicSerializer,
)


class SpendlyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = str(user.id)
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserPublicSerializer(self.user).data
        return data


class SpendlyTokenView(TokenObtainPairView):
    serializer_class = SpendlyTokenSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return ok(
            UserPublicSerializer(user).data,
            message="Registered successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class PersonalExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = PersonalExpenseSerializer
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Expense.objects.filter(
            created_by=self.request.user, kind=Expense.Kind.PERSONAL
        )

    def get_permissions(self):
        base = [IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return base + [IsExpenseOwnerForPersonal()]
        return base


class SpendGroupViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return SpendGroup.objects.filter(members=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return SpendGroupCreateSerializer
        return SpendGroupSerializer

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, pk=None):
        group = self.get_object()
        users = group.members.all().order_by("username")
        return Response(UserPublicSerializer(users, many=True).data)


class GroupExpenseListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfGroupFromUrl]

    def get_queryset(self):
        return Expense.objects.filter(
            group_id=self.kwargs["group_id"], kind=Expense.Kind.GROUP
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return GroupExpenseSerializer
        return GroupExpenseListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["group"] = get_object_or_404(SpendGroup, pk=self.kwargs["group_id"])
        return ctx

    def create(self, request, *args, **kwargs):
        group = get_object_or_404(SpendGroup, pk=self.kwargs["group_id"])
        ser = GroupExpenseSerializer(
            data=request.data, context={**self.get_serializer_context(), "group": group}
        )
        ser.is_valid(raise_exception=True)
        ser.save()
        return ok(
            GroupExpenseReadSerializer(ser.instance).data,
            status_code=status.HTTP_201_CREATED,
        )


class GroupExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = "expense_id"

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [IsAuthenticated(), IsGroupMember()]
        return [IsAuthenticated(), IsGroupMember(), IsGroupExpenseEditor()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GroupExpenseReadSerializer
        return ExpenseSerializer

    def get_object(self):
        obj = get_object_or_404(
            Expense,
            pk=self.kwargs["expense_id"],
            group_id=self.kwargs["group_id"],
            kind=Expense.Kind.GROUP,
        )
        self.check_object_permissions(self.request, obj)
        return obj


class GroupSplitMarkPaidView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfGroupFromUrl]

    def post(self, request, group_id, expense_id, split_id):
        expense = get_object_or_404(
            Expense,
            pk=expense_id,
            group_id=group_id,
            kind=Expense.Kind.GROUP,
        )
        if expense.created_by_id != request.user.id:
            return fail(
                "Only the person who added the expense can mark splits paid.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        split = get_object_or_404(GroupExpenseSplit, pk=split_id, expense=expense)
        split.status = GroupExpenseSplit.Status.PAID
        split.paid_at = timezone.now()
        split.save(update_fields=["status", "paid_at"])
        return ok(GroupExpenseSplitSerializer(split).data)


class GroupSplitMarkPendingView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfGroupFromUrl]

    def post(self, request, group_id, expense_id, split_id):
        expense = get_object_or_404(
            Expense,
            pk=expense_id,
            group_id=group_id,
            kind=Expense.Kind.GROUP,
        )
        if expense.created_by_id != request.user.id:
            return fail(
                "Only the person who added the expense can update split status.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        split = get_object_or_404(GroupExpenseSplit, pk=split_id, expense=expense)
        split.status = GroupExpenseSplit.Status.PENDING
        split.paid_at = None
        split.save(update_fields=["status", "paid_at"])
        return ok(GroupExpenseSplitSerializer(split).data)


class MyFinancesView(APIView):
    def get(self, request):
        user = request.user
        payable = (
            GroupExpenseSplit.objects.filter(
                owee=user, status=GroupExpenseSplit.Status.PENDING
            ).aggregate(t=Sum("share_amount"))["t"]
            or Decimal("0")
        )
        receivable = (
            GroupExpenseSplit.objects.filter(
                expense__created_by=user,
                status=GroupExpenseSplit.Status.PENDING,
            ).aggregate(t=Sum("share_amount"))["t"]
            or Decimal("0")
        )

        personal = Expense.objects.filter(
            created_by=user, kind=Expense.Kind.PERSONAL
        ).order_by("-spent_on")[:100]

        you_owe = (
            GroupExpenseSplit.objects.filter(
                owee=user, status=GroupExpenseSplit.Status.PENDING
            )
            .select_related("expense", "expense__group", "expense__created_by")
            .order_by("-expense__spent_on")[:100]
        )

        you_are_owed = (
            GroupExpenseSplit.objects.filter(
                expense__created_by=user,
                status=GroupExpenseSplit.Status.PENDING,
            )
            .select_related("expense", "owee", "expense__group")
            .order_by("-expense__spent_on")[:100]
        )

        def owe_row(s):
            return {
                "split_id": str(s.id),
                "share_amount": str(s.share_amount),
                "status": s.status,
                "payer_username": s.expense.created_by.username,
                "group_name": s.expense.group.name,
                "group_id": str(s.expense.group_id),
                "expense_id": str(s.expense_id),
                "description": s.expense.description,
                "spent_on": str(s.expense.spent_on),
            }

        def recv_row(s):
            return {
                "split_id": str(s.id),
                "share_amount": str(s.share_amount),
                "status": s.status,
                "owee_username": s.owee.username,
                "group_name": s.expense.group.name,
                "group_id": str(s.expense.group_id),
                "expense_id": str(s.expense_id),
                "description": s.expense.description,
                "spent_on": str(s.expense.spent_on),
            }

        return ok(
            {
                "payable_total": str(payable),
                "receivable_total": str(receivable),
                "personal_expenses": PersonalExpenseSerializer(personal, many=True).data,
                "you_owe": [owe_row(s) for s in you_owe],
                "you_are_owed": [recv_row(s) for s in you_are_owed],
            }
        )


class OverviewDashboardView(APIView):
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        month_start = date(today.year, today.month, 1)

        personal_month = (
            Expense.objects.filter(
                created_by=user,
                kind=Expense.Kind.PERSONAL,
                spent_on__gte=month_start,
                spent_on__lte=today,
            ).aggregate(t=Sum("amount"))["t"]
            or Decimal("0")
        )

        group_recorded_month = (
            Expense.objects.filter(
                created_by=user,
                kind=Expense.Kind.GROUP,
                spent_on__gte=month_start,
                spent_on__lte=today,
            ).aggregate(t=Sum("amount"))["t"]
            or Decimal("0")
        )

        month_total_recorded = personal_month + group_recorded_month

        payable_remaining = (
            GroupExpenseSplit.objects.filter(
                owee=user, status=GroupExpenseSplit.Status.PENDING
            ).aggregate(t=Sum("share_amount"))["t"]
            or Decimal("0")
        )

        receivable_pending = (
            GroupExpenseSplit.objects.filter(
                expense__created_by=user,
                status=GroupExpenseSplit.Status.PENDING,
            ).aggregate(t=Sum("share_amount"))["t"]
            or Decimal("0")
        )

        cat_totals = defaultdict(lambda: Decimal("0"))
        for e in Expense.objects.filter(
            created_by=user,
            spent_on__gte=month_start,
            spent_on__lte=today,
        ):
            key = (e.category or "").strip() or "Uncategorized"
            cat_totals[key] += e.amount

        category_spending = [
            {"category": k, "total": str(v)} for k, v in sorted(cat_totals.items(), key=lambda x: -x[1])
        ]

        return ok(
            {
                "month": f"{today.year}-{today.month:02d}",
                "month_total_recorded": str(month_total_recorded),
                "month_personal": str(personal_month),
                "month_group_you_paid": str(group_recorded_month),
                "payable_remaining": str(payable_remaining),
                "receivable_pending": str(receivable_pending),
                "category_spending": category_spending,
            }
        )


class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return User.objects.none()
        return (
            User.objects.filter(
                Q(username__icontains=q) | Q(display_name__icontains=q)
            )
            .exclude(pk=self.request.user.pk)
            .order_by("username")[:25]
        )


class GroupSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SpendGroupSerializer

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        base = SpendGroup.objects.filter(members=self.request.user).distinct()
        if len(q) < 1:
            return base.order_by("-created_at")[:50]
        return base.filter(name__icontains=q).order_by("-created_at")[:50]


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    # POST is required for mark-all-read and mark-read @action routes
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = Notification.objects.filter(
            user=request.user, read_at__isnull=True
        ).update(read_at=timezone.now())
        return ok({"updated": updated})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        n = get_object_or_404(Notification, pk=pk, user=request.user)
        if n.read_at is None:
            n.read_at = timezone.now()
            n.save(update_fields=["read_at"])
        return ok(NotificationSerializer(n).data)


class PendingInvitationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvitationSerializer

    def get_queryset(self):
        return GroupInvitation.objects.filter(
            invitee=self.request.user, status=GroupInvitation.Status.PENDING
        ).select_related("group", "inviter")


class GroupInviteCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfGroupFromUrl]
    serializer_class = CreateInviteSerializer

    def post(self, request, group_id):
        group = get_object_or_404(SpendGroup, pk=group_id)
        self.check_object_permissions(request, group)
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        uname = ser.validated_data["username"].strip().lower()
        invitee = get_object_or_404(User, username__iexact=uname)
        if invitee == request.user:
            return fail("You cannot invite yourself.", code="validation_error")
        if GroupMembership.objects.filter(group=group, user=invitee).exists():
            return fail("User is already in this group.", code="validation_error")
        if GroupInvitation.objects.filter(
            group=group,
            invitee=invitee,
            status=GroupInvitation.Status.PENDING,
        ).exists():
            return fail("An invitation is already pending.", code="validation_error")
        with transaction.atomic():
            inv = GroupInvitation.objects.create(
                group=group, inviter=request.user, invitee=invitee
            )
            Notification.objects.create(
                user=invitee,
                notification_type="group_invite",
                body=f"@{request.user.username} invited you to group “{group.name}”.",
                metadata={
                    "group_id": str(group.id),
                    "invitation_id": str(inv.id),
                },
            )
        return ok(
            InvitationSerializer(inv).data,
            message="Invitation sent.",
            status_code=status.HTTP_201_CREATED,
        )


class InvitationAcceptView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        inv = get_object_or_404(
            GroupInvitation,
            pk=invitation_id,
            invitee=request.user,
            status=GroupInvitation.Status.PENDING,
        )
        with transaction.atomic():
            inv.status = GroupInvitation.Status.ACCEPTED
            inv.save(update_fields=["status"])
            GroupMembership.objects.get_or_create(user=request.user, group=inv.group)
        return ok({"status": "accepted", "group_id": str(inv.group_id)})


class InvitationDeclineView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        inv = get_object_or_404(
            GroupInvitation,
            pk=invitation_id,
            invitee=request.user,
            status=GroupInvitation.Status.PENDING,
        )
        inv.status = GroupInvitation.Status.DECLINED
        inv.save(update_fields=["status"])
        return ok({"status": "declined"})


class GroupChatView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsMemberOfGroupFromUrl]

    def get(self, request, group_id):
        get_object_or_404(SpendGroup, pk=group_id)
        msgs = list(
            ChatMessage.objects.filter(group_id=group_id)
            .select_related("sender")
            .order_by("-created_at")[:200]
        )
        msgs.reverse()
        return ok(ChatMessageSerializer(msgs, many=True).data)

    def post(self, request, group_id):
        get_object_or_404(SpendGroup, pk=group_id)
        body = (request.data.get("body") or "").strip()
        if not body:
            return fail("Message body is required.", code="validation_error")
        msg = ChatMessage.objects.create(
            sender=request.user, group_id=group_id, body=body[:4000]
        )
        return ok(
            ChatMessageSerializer(msg).data,
            status_code=status.HTTP_201_CREATED,
        )


class DirectChatView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        other = get_object_or_404(User, pk=user_id)
        if other == request.user:
            return fail("Invalid recipient.", code="validation_error")
        msgs = (
            ChatMessage.objects.filter(
                Q(sender=request.user, recipient=other)
                | Q(sender=other, recipient=request.user)
            )
            .select_related("sender")
            .order_by("-created_at")[:200]
        )
        msgs = list(msgs)
        msgs.reverse()
        return ok(ChatMessageSerializer(msgs, many=True).data)

    def post(self, request, user_id):
        other = get_object_or_404(User, pk=user_id)
        if other == request.user:
            return fail("Invalid recipient.", code="validation_error")
        body = (request.data.get("body") or "").strip()
        if not body:
            return fail("Message body is required.", code="validation_error")
        msg = ChatMessage.objects.create(
            sender=request.user,
            recipient=other,
            body=body[:4000],
        )
        return ok(
            ChatMessageSerializer(msg).data,
            status_code=status.HTTP_201_CREATED,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_notification_count(request):
    n = Notification.objects.filter(user=request.user, read_at__isnull=True).count()
    return ok({"count": n})
