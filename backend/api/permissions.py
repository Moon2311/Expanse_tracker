from rest_framework.permissions import BasePermission

from api.models import GroupMembership, SpendGroup


class IsGroupMember(BasePermission):
    message = "You must be a member of this group."

    def has_object_permission(self, request, view, obj):
        group = obj if isinstance(obj, SpendGroup) else getattr(obj, "group", None)
        if group is None:
            return False
        return GroupMembership.objects.filter(
            group=group, user=request.user
        ).exists()


class IsMemberOfGroupFromUrl(BasePermission):
    message = "You must be a member of this group."

    def has_permission(self, request, view):
        gid = view.kwargs.get("group_id")
        if not gid:
            return False
        return GroupMembership.objects.filter(
            group_id=gid, user=request.user
        ).exists()


class IsExpenseOwnerForPersonal(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id


class IsGroupExpenseEditor(BasePermission):
    """Only the user who recorded the group expense may change it."""

    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id
