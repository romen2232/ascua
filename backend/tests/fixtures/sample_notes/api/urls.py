from rest_framework.routers import SimpleRouter

from tests.fixtures.sample_notes.api.views import SampleNoteViewSet

router = SimpleRouter()
router.register("notes", SampleNoteViewSet, basename="sample-note")
urlpatterns = router.urls
