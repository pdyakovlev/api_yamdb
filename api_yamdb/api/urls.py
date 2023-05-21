from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('titles', views.TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', views.RegisterUserView.as_view(), name='register'),
    path('v1/auth/token/', views.GetTokenView.as_view(), name='get_token'),
]
