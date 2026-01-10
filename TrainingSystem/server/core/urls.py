from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ★★★ 必须引入 SimpleJWT 的视图 ★★★
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
router.register(r'tasks', TrainingTaskViewSet, basename='tasks')
router.register(r'reports', StudentReportViewSet, basename='reports')

urlpatterns = [
    # 业务接口路由
    path('', include(router.urls)),
    
    # ★★★ 核心修复：添加登录和刷新 token 的路由 ★★★
    # 这样前端请求 /api/token/ 才能找到地方
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]