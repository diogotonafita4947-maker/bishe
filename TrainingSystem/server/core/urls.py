from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ★★★ 必须引入 SimpleJWT 的登录视图 ★★★
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, ClassGroupViewSet, ReportTemplateViewSet, 
    TrainingTaskViewSet, StudentReportViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'classes', ClassGroupViewSet)
router.register(r'templates', ReportTemplateViewSet)
router.register(r'tasks', TrainingTaskViewSet, basename='task')
router.register(r'reports', StudentReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    
    # ★★★ 补回丢失的登录接口 ★★★
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]