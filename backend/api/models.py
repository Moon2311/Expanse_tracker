import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)


class SpendGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_spend_groups"
    )
    members = models.ManyToManyField(
        User, through="GroupMembership", related_name="spend_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class GroupMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(SpendGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "group")]


class GroupInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        SpendGroup, on_delete=models.CASCADE, related_name="invitations"
    )
    inviter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invites_sent"
    )
    invitee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invites_received"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Expense(models.Model):
    class Kind(models.TextChoices):
        PERSONAL = "personal", "Personal"
        GROUP = "group", "Group"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
    spent_on = models.DateField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="expenses_created"
    )
    group = models.ForeignKey(
        SpendGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="expenses",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_on", "-created_at"]

    def clean(self):
        if self.kind == self.Kind.GROUP and self.group_id is None:
            raise ValidationError("Group expenses must reference a group.")
        if self.kind == self.Kind.PERSONAL and self.group_id is not None:
            raise ValidationError("Personal expenses cannot have a group.")


class GroupExpenseSplit(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="splits",
    )
    owee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="group_expense_splits_owed",
    )
    share_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = [("expense", "owee")]


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=64, db_column="type")
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_messages_sent"
    )
    group = models.ForeignKey(
        SpendGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_messages",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_messages_received",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def clean(self):
        g, r = self.group_id, self.recipient_id
        if bool(g) == bool(r):
            raise ValidationError("Set exactly one of group or recipient (direct).")
