import secrets
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from identity.api import serializers as s
from identity.application.deps import SignUpDeps
from identity.application.invite import invite_user
from identity.application.sign_up import accept_invitation, confirm_totp
from identity.domain.email import Email
from identity.infrastructure.repositories import (
    DjangoInvitationRepository,
    DjangoUserRepository,
    SystemClock,
)
from identity.infrastructure.tokens import SignedEnrolmentTokens
from identity.infrastructure.totp import DjangoOtpTotp
from shared_kernel.api.scoped import actor_from_request


def sign_up_deps() -> SignUpDeps:
    return SignUpDeps(
        users=DjangoUserRepository(),
        invitations=DjangoInvitationRepository(),
        clock=SystemClock(),
        totp=DjangoOtpTotp(),
        enrolment=SignedEnrolmentTokens(),
    )


def _valid(serializer_class: Any, request: Request) -> dict[str, Any]:
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    return dict(serializer.validated_data)


class InvitationCreateView(APIView):
    @extend_schema(request=s.InviteRequest, responses={201: s.InviteResponse})
    def post(self, request: Request) -> Response:
        data = _valid(s.InviteRequest, request)
        token = invite_user(
            actor_from_request(request),
            Email(data["email"]),
            sign_up_deps(),
            token_factory=lambda: secrets.token_urlsafe(32),
        )
        return Response({"token": token}, status=status.HTTP_201_CREATED)


class InvitationAcceptView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(request=s.AcceptInvitationRequest, responses={201: s.TotpEnrolmentResponse})
    def post(self, request: Request) -> Response:
        data = _valid(s.AcceptInvitationRequest, request)
        enrolment = accept_invitation(
            data["token"], data["display_name"], data["password"], data["locale"], sign_up_deps()
        )
        body = {
            "user_id": str(enrolment.user_id),
            "provisioning_uri": enrolment.provisioning_uri,
            "enrolment_token": enrolment.enrolment_token,
        }
        return Response(body, status=status.HTTP_201_CREATED)


class TotpConfirmView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(request=s.ConfirmTotpRequest, responses={204: None})
    def post(self, request: Request) -> Response:
        data = _valid(s.ConfirmTotpRequest, request)
        confirm_totp(data["enrolment_token"], data["code"], sign_up_deps())
        return Response(status=status.HTTP_204_NO_CONTENT)
