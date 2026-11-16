from django.urls import path

from identity.api import views

urlpatterns = [
    path("invitations", views.InvitationCreateView.as_view(), name="invitation-create"),
    path("invitations/accept", views.InvitationAcceptView.as_view(), name="invitation-accept"),
    path("auth/totp/confirm", views.TotpConfirmView.as_view(), name="totp-confirm"),
]
