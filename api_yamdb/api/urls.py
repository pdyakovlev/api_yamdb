from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TitleViewSet, ReviewViewSet

router = DefaultRouter()

router.register('titles', TitleViewSet, basename='titles')
router.register('titles/<int:title_id>/reviews',
                ReviewViewSet, basename='reviews')

urlpatterns = [
    path('v1/', include(router.urls))
]
