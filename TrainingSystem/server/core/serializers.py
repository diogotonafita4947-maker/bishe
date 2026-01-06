from rest_framework import serializers
from .models import User, ReportTemplate, TrainingTask, StudentReport, ClassGroup, ReportAttachment

# 班级
class ClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = '__all__'
        read_only_fields = ['created_by']

# 用户
class UserSerializer(serializers.ModelSerializer):
    class_group_name = serializers.CharField(source='class_group.name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'student_id', 'class_group', 'class_group_name']

# 模板
class ReportTemplateSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    class Meta:
        model = ReportTemplate
        fields = '__all__'

# 任务
class TrainingTaskSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)
    template_title = serializers.CharField(source='template.title', read_only=True)
    reference_materials_details = ReportTemplateSerializer(source='reference_materials', many=True, read_only=True)

    class Meta:
        model = TrainingTask
        fields = '__all__'
        read_only_fields = ['teacher']

# ★★★ 新增：附件序列化器 ★★★
class ReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAttachment
        fields = ['id', 'file', 'uploaded_at']

# 报告
class StudentReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    # ★★★ 返回附件列表 ★★★
    attachments_list = ReportAttachmentSerializer(source='attachments', many=True, read_only=True)
    
    class Meta:
        model = StudentReport
        fields = '__all__'
        read_only_fields = ['student', 'submitted_at']