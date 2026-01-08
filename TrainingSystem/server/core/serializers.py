import random
import string
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    User, ReportTemplate, TrainingTask, StudentReport, 
    ClassGroup, ReportAttachment, 
    StudentWhitelist, TeacherWhitelist
)

class ClassGroupSerializer(serializers.ModelSerializer):
    # 增加一个字段显示老师名字
    teacher_name = serializers.CharField(source='created_by.first_name', read_only=True)
    
    class Meta:
        model = ClassGroup
        fields = '__all__'
        read_only_fields = ['created_by', 'invite_code']

class UserSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(source='first_name', read_only=True)
    # ★★★ 修改：返回所有加入的班级列表 ★★★
    joined_classes = ClassGroupSerializer(source='classes', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'role', 'student_id', 'joined_classes']

class ReportTemplateSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    class Meta:
        model = ReportTemplate
        fields = '__all__'

class TrainingTaskSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)
    template_title = serializers.CharField(source='template.title', read_only=True)
    reference_materials_details = ReportTemplateSerializer(source='reference_materials', many=True, read_only=True)
    class Meta:
        model = TrainingTask
        fields = '__all__'
        read_only_fields = ['teacher']

class ReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAttachment
        fields = ['id', 'file', 'uploaded_at']

class StudentReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    student_number = serializers.CharField(source='student.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    attachments_list = ReportAttachmentSerializer(source='attachments', many=True, read_only=True)
    class Meta:
        model = StudentReport
        fields = '__all__'
        read_only_fields = ['student', 'submitted_at']

class StudentWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWhitelist
        fields = '__all__'

class TeacherWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherWhitelist
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    student_id = serializers.CharField(required=False, allow_blank=True) 
    
    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'role', 'student_id']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("两次密码不一致")
        role = data.get('role')
        name_input = data.get('student_id')
        id_input = data.get('username')

        if role == 'student':
            try:
                white_obj = StudentWhitelist.objects.get(student_id=id_input)
            except StudentWhitelist.DoesNotExist:
                raise serializers.ValidationError("该学号不在学校名单中，请联系管理员")
            if white_obj.name != name_input:
                raise serializers.ValidationError("姓名与学号不匹配，请核对")
            if white_obj.is_registered:
                raise serializers.ValidationError("该学号已被注册")
            data['whitelist_obj'] = white_obj
        elif role == 'teacher':
            try:
                white_obj = TeacherWhitelist.objects.get(teacher_id=id_input)
            except TeacherWhitelist.DoesNotExist:
                raise serializers.ValidationError("该工号不在教师名单中")
            if white_obj.name != name_input:
                raise serializers.ValidationError("姓名与工号不匹配")
            if white_obj.is_registered:
                raise serializers.ValidationError("该教师号已被注册")
            data['whitelist_obj'] = white_obj
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        whitelist_obj = validated_data.pop('whitelist_obj')
        user_name_input = validated_data.pop('student_id') 
        account_id = validated_data['username']            
        
        validated_data['password'] = make_password(validated_data['password'])
        
        user = User.objects.create(
            username=account_id,
            password=validated_data['password'],
            role=validated_data['role'],
            student_id=account_id, 
            first_name=user_name_input
        )
        whitelist_obj.is_registered = True
        whitelist_obj.save()
        return user