from django.urls import path

from identity.api import views

urlpatterns = [
    path("invitations", views.InvitationCreateView.as_view(), name="invitation-create"),
    path("invitations/accept", views.InvitationAcceptView.as_view(), name="invitation-accept"),
    path("auth/totp/confirm", views.TotpConfirmView.as_view(), name="totp-confirm"),
    path("auth/sign-in", views.SignInView.as_view(), name="sign-in"),
    path("auth/sign-in/totp", views.SignInTotpView.as_view(), name="sign-in-totp"),
    path("auth/refresh", views.RefreshView.as_view(), name="token-refresh"),
    path("auth/sign-out", views.SignOutView.as_view(), name="sign-out"),
    path("me", views.MeView.as_view(), name="me"),
]
