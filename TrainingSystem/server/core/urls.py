from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, 
    ReportTemplateViewSet, 
    TrainingTaskViewSet, 
    StudentReportViewSet,
    ClassGroupViewSet  # ★ 别忘了引入班级视图，否则后面会报错
)

router = DefaultRouter()

# 1. 用户与班级
router.register(r'users', UserViewSet)
router.register(r'classes', ClassGroupViewSet)

# 2. 模板
router.register(r'templates', ReportTemplateViewSet)

# 3. 任务 (★ 关键修复：加上 basename='task')
# 因为 views.py 里的 TrainingTaskViewSet 用了 get_queryset，所以这里必须加名字
router.register(r'tasks', TrainingTaskViewSet, basename='task')

# 4. 报告 (之前已修复，保持不变)
router.register(r'reports', StudentReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]