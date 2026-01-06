from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from .models import User, ReportTemplate, TrainingTask, StudentReport, ClassGroup, ReportAttachment
from .serializers import (
    UserSerializer, 
    ReportTemplateSerializer, 
    TrainingTaskSerializer, 
    StudentReportSerializer,
    ClassGroupSerializer,
    ReportAttachmentSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.all()
        class_group_id = self.request.query_params.get('class_group')
        if class_group_id:
            return queryset.filter(class_group_id=class_group_id)
        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ClassGroupViewSet(viewsets.ModelViewSet):
    queryset = ClassGroup.objects.all()
    serializer_class = ClassGroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=['post'])
    def upload_docx(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "请选择文件"}, status=400)
        template_title = file_obj.name.split('.')[0]
        mock_structure = [
            {"type": "header", "value": "一、实训基本信息"},
            {"type": "input", "label": "实训名称", "value": template_title}, 
            {"type": "input", "label": "实训地点", "placeholder": "请输入地点"},
            {"type": "header", "value": "二、实训内容"},
            {"type": "textarea", "label": "实训目的", "placeholder": "请输入目的..."},
            {"type": "textarea", "label": "实训步骤", "placeholder": "请输入步骤..."},
            {"type": "header", "value": "三、总结"},
            {"type": "textarea", "label": "心得体会", "placeholder": "请输入心得..."}
        ]
        new_template = ReportTemplate.objects.create(
            title=f"{template_title} (导入版)", type='report',
            created_by=request.user, content_structure=mock_structure
        )
        return Response({"id": new_template.id, "title": new_template.title, "message": "解析成功！"})

class TrainingTaskViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: return TrainingTask.objects.none()
        if user.role in ['teacher', 'admin'] or user.is_superuser:
            return TrainingTask.objects.filter(teacher=user)
        if user.class_group:
            return TrainingTask.objects.filter(target_class=user.class_group)
        return TrainingTask.objects.none()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        task = self.get_object()
        students = User.objects.filter(class_group=task.target_class, role='student')
        stats_list = []
        for student in students:
            report = StudentReport.objects.filter(task=task, student=student).first()
            stats_list.append({
                'student_id': student.id,
                'student_name': student.username,
                'student_number': student.student_id,
                'status': report.status if report else 'unsubmitted',
                'score': report.score if report else None,
                'report_id': report.id if report else None,
                'submitted_at': report.submitted_at if report else None
            })
        return Response(stats_list)

class StudentReportViewSet(viewsets.ModelViewSet):
    serializer_class = StudentReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: return StudentReport.objects.none()
        queryset = StudentReport.objects.all()
        task_id = self.request.query_params.get('task')
        if task_id: queryset = queryset.filter(task_id=task_id)
        if user.role == 'teacher' or user.is_superuser: return queryset
        return queryset.filter(student=user)

    # ★★★ 核心修改：处理多附件上传 ★★★
    def perform_create(self, serializer):
        report = serializer.save(student=self.request.user)
        self._handle_attachments(report)

    def perform_update(self, serializer):
        report = serializer.save()
        self._handle_attachments(report)
        
    def _handle_attachments(self, report):
        files = self.request.FILES.getlist('new_attachments') # 获取前端的多文件
        for f in files:
            ReportAttachment.objects.create(report=report, file=f)
            
    # ★★★ 新增：删除单个附件 ★★★
    @action(detail=True, methods=['delete'])
    def remove_attachment(self, request, pk=None):
        att_id = request.query_params.get('attachment_id')
        if att_id:
            ReportAttachment.objects.filter(id=att_id, report_id=pk).delete()
        return Response({'status': 'success'})