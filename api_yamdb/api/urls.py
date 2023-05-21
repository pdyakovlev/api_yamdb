from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('titles', views.TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                views.ReviewViewSet,
                basename='reviews'
                )

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
    path('v1/auth/signup/', views.RegisterUserView.as_view(), name='register'),
    path('v1/auth/token/', views.GetTokenView.as_view(), name='get_token'),
]
