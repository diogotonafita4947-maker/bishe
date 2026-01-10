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
    teacher_name = serializers.CharField(source='created_by.first_name', read_only=True)
    class Meta:
        model = ClassGroup
        fields = '__all__'
        read_only_fields = ['created_by', 'invite_code']

class UserSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(source='first_name', read_only=True)
    joined_classes = ClassGroupSerializer(source='classes', many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'role', 'student_id', 'joined_classes']

class ReportTemplateSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    class Meta:
        model = ReportTemplate
        fields = '__all__'

# ★★★ 修复重点：增加防崩溃判断 ★★★
class TrainingTaskSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)
    template_title = serializers.CharField(source='template.title', read_only=True)
    template_structure = serializers.JSONField(source='template.content_structure', read_only=True)
    reference_materials_details = ReportTemplateSerializer(source='reference_materials', many=True, read_only=True)

    my_status = serializers.SerializerMethodField()
    my_score = serializers.SerializerMethodField()

    class Meta:
        model = TrainingTask
        fields = '__all__'
        read_only_fields = ['teacher']

    def get_teacher_name(self, obj):
        return obj.teacher.first_name if obj.teacher.first_name else obj.teacher.username

    def get_my_status(self, obj):
        # 安全获取 request，防止 AttributeError
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return 'unsubmitted'
        
        user = request.user
        if user.role != 'student': return 'unsubmitted'
        
        # 尝试获取报告
        report = obj.studentreport_set.filter(student=user).first()
        return report.status if report else 'unsubmitted'

    def get_my_score(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
            
        user = request.user
        if user.role != 'student': return None
        
        report = obj.studentreport_set.filter(student=user).first()
        return report.score if report else None

class ReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAttachment
        fields = ['id', 'file', 'uploaded_at']

class StudentReportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    student_number = serializers.CharField(source='student.username', read_only=True)
    student_class = serializers.CharField(source='task.target_class.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_end_time = serializers.DateTimeField(source='task.end_time', read_only=True)
    task_max_submissions = serializers.IntegerField(source='task.max_submissions', read_only=True)
    
    template_structure = serializers.SerializerMethodField()
    attachments_list = ReportAttachmentSerializer(source='attachments', many=True, read_only=True)
    
    class Meta:
        model = StudentReport
        fields = '__all__'
        read_only_fields = ['student', 'submitted_at', 'graded_at', 'score', 'feedback', 'submit_count']

    def get_teacher_name(self, obj):
        t = obj.task.teacher
        return t.first_name if t.first_name else t.username

    def get_template_structure(self, obj):
        raw_struct = obj.task.template.content_structure
        teacher_filled = obj.task.task_context or {}
        merged_struct = []
        if not isinstance(raw_struct, list): return []
        
        for item in raw_struct:
            new_item = item.copy()
            if item.get('type') == 'teacher_block':
                label = item.get('label')
                if label and label in teacher_filled:
                    new_item['value'] = teacher_filled[label]
                else:
                    new_item['value'] = "(老师未填写)"
            merged_struct.append(new_item)
        return merged_struct

class StudentWhitelistSerializer(serializers.ModelSerializer):
    class Meta: model = StudentWhitelist; fields = '__all__'

class TeacherWhitelistSerializer(serializers.ModelSerializer):
    class Meta: model = TeacherWhitelist; fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    student_id = serializers.CharField(required=False, allow_blank=True) 
    class Meta: model = User; fields = ['username', 'password', 'confirm_password', 'role', 'student_id']

    def validate(self, data):
        if data['password'] != data['confirm_password']: raise serializers.ValidationError("两次密码不一致")
        role = data.get('role'); name_input = data.get('student_id'); id_input = data.get('username')
        
        if role == 'student':
            try: white_obj = StudentWhitelist.objects.get(student_id=id_input)
            except: raise serializers.ValidationError("该学号不在学校名单中")
            if white_obj.name != name_input: raise serializers.ValidationError("姓名与学号不匹配")
            if white_obj.is_registered: raise serializers.ValidationError("该学号已被注册")
            data['whitelist_obj'] = white_obj
        elif role == 'teacher':
            try: white_obj = TeacherWhitelist.objects.get(teacher_id=id_input)
            except: raise serializers.ValidationError("该工号不在教师名单中")
            if white_obj.name != name_input: raise serializers.ValidationError("姓名与工号不匹配")
            if white_obj.is_registered: raise serializers.ValidationError("该教师号已被注册")
            data['whitelist_obj'] = white_obj
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password'); whitelist_obj = validated_data.pop('whitelist_obj')
        user_name_input = validated_data.pop('student_id'); account_id = validated_data['username']            
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(username=account_id, password=validated_data['password'], role=validated_data['role'], student_id=account_id, first_name=user_name_input)
        whitelist_obj.is_registered = True; whitelist_obj.save()
        return user