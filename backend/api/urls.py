from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api import views

router = DefaultRouter()
router.register("expenses", views.PersonalExpenseViewSet, basename="personal-expense")
router.register("groups", views.SpendGroupViewSet, basename="spend-group")
router.register("notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.SpendlyTokenView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("me/finances/", views.MyFinancesView.as_view(), name="me-finances"),
    path("me/overview/", views.OverviewDashboardView.as_view(), name="me-overview"),
    path("search/users/", views.UserSearchView.as_view(), name="search-users"),
    path("search/groups/", views.GroupSearchView.as_view(), name="search-groups"),
    path("invitations/pending/", views.PendingInvitationListView.as_view(), name="invitations-pending"),
    path(
        "invitations/<uuid:invitation_id>/accept/",
        views.InvitationAcceptView.as_view(),
        name="invitation-accept",
    ),
    path(
        "invitations/<uuid:invitation_id>/decline/",
        views.InvitationDeclineView.as_view(),
        name="invitation-decline",
    ),
    path(
        "groups/<uuid:group_id>/expenses/",
        views.GroupExpenseListCreateView.as_view(),
        name="group-expenses-list",
    ),
    path(
        "groups/<uuid:group_id>/expenses/<uuid:expense_id>/",
        views.GroupExpenseDetailView.as_view(),
        name="group-expense-detail",
    ),
    path(
        "groups/<uuid:group_id>/expenses/<uuid:expense_id>/splits/<uuid:split_id>/mark-paid/",
        views.GroupSplitMarkPaidView.as_view(),
        name="group-split-mark-paid",
    ),
    path(
        "groups/<uuid:group_id>/expenses/<uuid:expense_id>/splits/<uuid:split_id>/mark-pending/",
        views.GroupSplitMarkPendingView.as_view(),
        name="group-split-mark-pending",
    ),
    path(
        "groups/<uuid:group_id>/invites/",
        views.GroupInviteCreateView.as_view(),
        name="group-invite",
    ),
    path(
        "groups/<uuid:group_id>/chat/",
        views.GroupChatView.as_view(),
        name="group-chat",
    ),
    path(
        "chat/direct/<uuid:user_id>/",
        views.DirectChatView.as_view(),
        name="direct-chat",
    ),
    path(
        "notifications/unread-count/",
        views.unread_notification_count,
        name="notifications-unread-count",
    ),
]

urlpatterns += router.urls
