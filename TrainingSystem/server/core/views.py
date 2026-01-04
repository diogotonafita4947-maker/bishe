from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, ReportTemplate, TrainingTask, StudentReport
from .serializers import UserSerializer, ReportTemplateSerializer, TrainingTaskSerializer, StudentReportSerializer

# User视图 (补全漏掉的User视图)
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

# 3. 报告视图 (这里是之前报错的重灾区)
class StudentReportViewSet(viewsets.ModelViewSet):
    serializer_class = StudentReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # ★★★ 安全气囊 1：如果用户对象不存在或未登录，直接返回空，防止后续代码崩溃
        if not user or not user.is_authenticated:
            return StudentReport.objects.none()

        # ★★★ 安全气囊 2：使用 getattr 获取 role，防止 user 对象因某种原因缺失 role 属性导致报错
        user_role = getattr(user, 'role', '')
        
        # 逻辑：老师或管理员看所有，学生看自己
        if user_role == 'teacher' or user.is_superuser:
            return StudentReport.objects.all()
        
        return StudentReport.objects.filter(student=user)

    def perform_create(self, serializer):
        # 自动填入当前登录的学生
        serializer.save(student=self.request.user)