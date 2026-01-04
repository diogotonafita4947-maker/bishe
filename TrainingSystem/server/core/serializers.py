from rest_framework import serializers
from .models import User, ReportTemplate, TrainingTask, StudentReport

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'student_id']

class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = '__all__'

class TrainingTaskSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    class Meta:
        model = TrainingTask
        fields = '__all__'

class StudentReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    class Meta:
        model = StudentReport
        fields = '__all__'
        # ★ 关键：让 student 字段只读，不需要前端传
        read_only_fields = ['student', 'submitted_at']