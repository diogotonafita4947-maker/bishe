from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, ReportTemplate, TrainingTask, StudentReport
from .serializers import UserSerializer, ReportTemplateSerializer, TrainingTaskSerializer, StudentReportSerializer

# ★ 补回了漏掉的 UserViewSet
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

# 1. 模板视图
class ReportTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]

# 2. 任务视图
class TrainingTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainingTask.objects.all()
    serializer_class = TrainingTaskSerializer
    permission_classes = [IsAuthenticated]

# 3. 报告视图
class StudentReportViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher' or user.is_superuser:
            return StudentReport.objects.all()
        return StudentReport.objects.filter(student=user)

    serializer_class = StudentReportSerializer
    permission_classes = [IsAuthenticated]

    # 自动填入当前登录的学生
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)