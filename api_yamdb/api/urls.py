from rest_framework.routers import DefaultRouter

from django.urls import include, path

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
router.register('genres', views.GenreViewSet, basename='genres')
router.register('categories', views.CategoryViewSet,
                basename='category-list-create')
router.register('categories/<slug:slug>', views.CategoryViewSet,
                basename='category-delete')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', views.RegisterUserView.as_view(), name='register'),
    path('v1/auth/token/', views.GetTokenView.as_view(), name='get_token'),
]
