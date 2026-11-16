from typing import Any

from django.db import models
from rest_framework import mixins, serializers

from shared_kernel.api.scoped import ScopedViewSet
from shared_kernel.domain.actor import Actor
from shared_kernel.domain.errors import InvalidValue
from tests.fixtures.sample_notes.infrastructure.models import SampleNote


class SampleNoteSerializer(serializers.ModelSerializer[SampleNote]):
    class Meta:
        model = SampleNote
        fields = ("id", "text")
        extra_kwargs = {"text": {"trim_whitespace": False}}  # noqa: RUF012


class SampleNoteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    ScopedViewSet,
):
    serializer_class = SampleNoteSerializer

    def repository_queryset(self, actor: Actor) -> models.QuerySet[Any]:
        return SampleNote.objects.for_actor(actor).order_by("text")

    def perform_create(self, serializer: Any) -> None:
        if not serializer.validated_data["text"].strip():
            raise InvalidValue("blank note")
        serializer.instance = SampleNote.objects.for_actor(self.actor).create(
            owner_id=self.actor.user_id, **serializer.validated_data
        )
