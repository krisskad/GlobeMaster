from django.urls import path, include
from rest_framework import routers
from .views import UploadViewSet, WordFrequencySet, NewsLookupSet

router = routers.DefaultRouter()
router.register(r'upload', UploadViewSet, basename="upload")
router.register(r'word_frequency', WordFrequencySet, basename="word_frequency")
router.register(r'news_lookup', NewsLookupSet, basename="find_mentioned")


# Wire up our API using automatic URL routing.
urlpatterns = [
    path('', include(router.urls)),
]