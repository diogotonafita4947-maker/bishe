from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 这里引用 views 才是对的，因为 views.py 就在它隔壁
from .views import UserViewSet, ReportTemplateViewSet, TrainingTaskViewSet, StudentReportViewSet

router = DefaultRouter()

# 注册 4 个接口
router.register(r'users', UserViewSet)
router.register(r'templates', ReportTemplateViewSet)
router.register(r'tasks', TrainingTaskViewSet)
# ★ 重点：给动态的 reports 加上 basename
router.register(r'reports', StudentReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]