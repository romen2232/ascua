from rest_framework import serializers


class InviteRequest(serializers.Serializer[None]):
    email = serializers.CharField(max_length=254)


class InviteResponse(serializers.Serializer[None]):
    token = serializers.CharField()


class AcceptInvitationRequest(serializers.Serializer[None]):
    token = serializers.CharField(max_length=200)
    display_name = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=200, trim_whitespace=False)
    locale = serializers.ChoiceField(choices=["es", "en"])


class TotpEnrolmentResponse(serializers.Serializer[None]):
    user_id = serializers.UUIDField()
    provisioning_uri = serializers.CharField()
    enrolment_token = serializers.CharField()


class ConfirmTotpRequest(serializers.Serializer[None]):
    enrolment_token = serializers.CharField(max_length=500)
    code = serializers.RegexField(r"^\d{6}$")
