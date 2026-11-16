import secrets
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from identity.api import messages  # noqa: F401  (registers error messages)
from identity.api import serializers as s
from identity.application.deps import SignUpDeps
from identity.application.invite import invite_user
from identity.application.sign_in import SignInDeps, finish_sign_in, start_sign_in
from identity.application.sign_up import accept_invitation, confirm_totp
from identity.domain.email import Email
from identity.infrastructure.credentials import DjangoCredentialChecker
from identity.infrastructure.repositories import (
    DjangoInvitationRepository,
    DjangoUserRepository,
    SystemClock,
)
from identity.infrastructure.tokens import SignedEnrolmentTokens, SignedMfaTokens, issue_session
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


REFRESH_COOKIE = "ascua_refresh"
# Covers /api/auth/refresh and /api/auth/sign-out: browsers only send a cookie under its Path.
REFRESH_COOKIE_PATH = "/api/auth/"


def _is_web(request: Request) -> bool:
    return request.headers.get("X-Ascua-Client") == "web"


def _session_response(request: Request, access: str, refresh: str) -> Response:
    """Native clients get the refresh token in the body; web clients only as an HttpOnly cookie."""
    if not _is_web(request):
        return Response({"access": access, "refresh": refresh})
    response = Response({"access": access})
    response.set_cookie(
        REFRESH_COOKIE,
        refresh,
        max_age=int(RefreshToken.lifetime.total_seconds()),
        path=REFRESH_COOKIE_PATH,
        secure=True,
        httponly=True,
        samesite="Strict",
    )
    return response


def _refresh_token_from(request: Request) -> str:
    body = request.data if isinstance(request.data, dict) else {}
    token = body.get("refresh") or request.COOKIES.get(REFRESH_COOKIE)
    if not token:
        raise InvalidToken("No refresh token")
    return str(token)


def sign_in_deps(request: Request) -> SignInDeps:
    return SignInDeps(
        users=DjangoUserRepository(),
        credentials=DjangoCredentialChecker(request._request),
        totp=DjangoOtpTotp(),
        mfa=SignedMfaTokens(),
    )


class SignInView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(request=s.SignInRequest, responses={200: s.SignInResponse})
    def post(self, request: Request) -> Response:
        data = _valid(s.SignInRequest, request)
        mfa_token = start_sign_in(data["email"], data["password"], sign_in_deps(request))
        return Response({"mfa_token": mfa_token})


class SignInTotpView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(request=s.SignInTotpRequest, responses={200: s.SessionResponse})
    def post(self, request: Request) -> Response:
        data = _valid(s.SignInTotpRequest, request)
        user_id = finish_sign_in(data["mfa_token"], data["code"], sign_in_deps(request))
        access, refresh = issue_session(user_id)
        return _session_response(request, access, refresh)


class _RefreshTokenView(APIView):
    """Authenticated by the refresh token itself; a bad token is a 401, not a 403."""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get_authenticate_header(self, request: Request) -> str:
        return 'Bearer realm="api"'


class RefreshView(_RefreshTokenView):
    @extend_schema(request=s.RefreshRequest, responses={200: s.SessionResponse})
    def post(self, request: Request) -> Response:
        serializer = TokenRefreshSerializer(data={"refresh": _refresh_token_from(request)})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc
        tokens = serializer.validated_data
        return _session_response(request, tokens["access"], tokens["refresh"])


class SignOutView(_RefreshTokenView):
    @extend_schema(request=s.RefreshRequest, responses={204: None})
    def post(self, request: Request) -> Response:
        """Revoke the refresh token if one is sent; always clear the web cookie."""
        body = request.data if isinstance(request.data, dict) else {}
        token = body.get("refresh") or request.COOKIES.get(REFRESH_COOKIE)
        if token:
            try:
                RefreshToken(token).blacklist()  # type: ignore[arg-type]
            except TokenError as exc:
                raise InvalidToken(str(exc)) from exc
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH, samesite="Strict")
        return response


class MeView(APIView):
    @extend_schema(responses={200: s.MeResponse})
    def get(self, request: Request) -> Response:
        user = DjangoUserRepository().get(actor_from_request(request).user_id)
        return Response(
            {
                "id": str(user.id),
                "email": user.email.value,
                "display_name": user.display_name,
                "locale": user.locale,
                "is_admin": user.is_admin,
            }
        )
