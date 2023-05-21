from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    'titles',
    views.TitleViewSet,
    basename='titles'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router.register(
    'users',
    views.UserViewSet,
    basename='users'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)
router.register('genres', views.GenreViewsSet, basename='genres')

urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/categories/',
        views.CategoryListCreateView.as_view(),
        name='category-list-create'
    ),
    path(
        'v1/categories/<slug:slug>/',
        views.CategoryDestroyView.as_view(),
        name='category-delete'
    ),
]
