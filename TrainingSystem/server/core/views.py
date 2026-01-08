import openpyxl
import random
import string
from docx import Document  # ★★★ 必须先 pip install python-docx
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser

from .models import (
    User, ReportTemplate, TrainingTask, StudentReport, ClassGroup, ReportAttachment,
    StudentWhitelist, TeacherWhitelist
)
from .serializers import (
    UserSerializer, ReportTemplateSerializer, TrainingTaskSerializer, 
    StudentReportSerializer, ClassGroupSerializer, ReportAttachmentSerializer,
    UserRegistrationSerializer,
    StudentWhitelistSerializer, TeacherWhitelistSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    # 注册接口 (纯净版，不再自动加群)
    @action(detail=False, methods=['post'], permission_classes=[]) 
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "username": user.username,
                "role": user.role,
                "message": "注册成功！请登录后加入班级。"
            })
        return Response(serializer.errors, status=400)

    # 管理员导入名单 (包含去小数点逻辑)
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser]) 
    def upload_roster(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj: return Response({"error": "未接收到文件"}, status=400)
        if not file_obj.name.endswith('.xlsx'): return Response({"error": "格式错误：仅支持 .xlsx"}, status=400)
            
        try:
            wb = openpyxl.load_workbook(file_obj, data_only=True) 
            sheet = wb.active
            s_new, s_old, t_new, t_old = 0, 0, 0, 0
            
            def clean_data(val):
                if val is None: return ""
                if isinstance(val, (int, float)): return str(int(val))
                return str(val).strip()

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row or not any(row): continue
                name = clean_data(row[0])
                uid = clean_data(row[1])
                if not name or not uid: continue 
                
                is_student = False
                class_name = ""
                if len(row) >= 3 and row[2]:
                    raw_cls = clean_data(row[2])
                    if raw_cls and raw_cls.lower() != 'none':
                        is_student = True
                        class_name = raw_cls

                if is_student:
                    _, created = StudentWhitelist.objects.update_or_create(
                        student_id=uid,
                        defaults={'name': name, 'class_name': class_name}
                    )
                    if created: s_new += 1
                    else: s_old += 1
                else:
                    _, created = TeacherWhitelist.objects.update_or_create(
                        teacher_id=uid,
                        defaults={'name': name}
                    )
                    if created: t_new += 1
                    else: t_old += 1
            
            msg = f"学生(新{s_new}/旧{s_old})，教师(新{t_new}/旧{t_old})"
            return Response({"message": f"导入成功！{msg}"})
        except Exception as e:
            return Response({"error": f"解析失败: {str(e)}"}, status=400)

    # 白名单管理接口
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def get_whitelist(self, request):
        students = StudentWhitelist.objects.all().order_by('class_name', 'student_id')
        teachers = TeacherWhitelist.objects.all().order_by('teacher_id')
        return Response({
            "students": StudentWhitelistSerializer(students, many=True).data,
            "teachers": TeacherWhitelistSerializer(teachers, many=True).data
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def add_whitelist_item(self, request):
        role = request.data.get('role')
        name = request.data.get('name')
        uid = request.data.get('uid')
        class_name = request.data.get('class_name', '')
        if not name or not uid: return Response({"error": "缺失必填项"}, status=400)

        if role == 'student':
            if StudentWhitelist.objects.filter(student_id=uid).exists(): return Response({"error": "学号已存在"}, status=400)
            StudentWhitelist.objects.create(name=name, student_id=uid, class_name=class_name)
        else:
            if TeacherWhitelist.objects.filter(teacher_id=uid).exists(): return Response({"error": "工号已存在"}, status=400)
            TeacherWhitelist.objects.create(name=name, teacher_id=uid)
        return Response({"message": "添加成功"})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def delete_whitelist_item(self, request):
        role = request.data.get('role')
        try:
            if role == 'student': StudentWhitelist.objects.filter(id=request.data.get('id')).delete()
            else: TeacherWhitelist.objects.filter(id=request.data.get('id')).delete()
            return Response({"message": "删除成功"})
        except: return Response({"error": "删除失败"}, status=400)


# 班级管理 (强制随机码)
class ClassGroupViewSet(viewsets.ModelViewSet):
    queryset = ClassGroup.objects.all()
    serializer_class = ClassGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin': return ClassGroup.objects.all()
        if user.role == 'teacher': return ClassGroup.objects.filter(created_by=user)
        if user.role == 'student': return user.classes.all()
        return ClassGroup.objects.none()

    def perform_create(self, serializer):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # 死循环检测，确保唯一
        while ClassGroup.objects.filter(invite_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        serializer.save(created_by=self.request.user, invite_code=code)

    @action(detail=False, methods=['post'])
    def join_class(self, request):
        code = request.data.get('invite_code', '').strip().upper()
        group = ClassGroup.objects.filter(invite_code=code).first()
        if not group: return Response({"error": "无效的邀请码"}, status=404)
        
        user = request.user
        if group in user.classes.all(): return Response({"error": "你已经在这个班级了"}, status=400)
        
        user.classes.add(group)
        return Response({"message": f"成功加入：{group.name}"})

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        group = self.get_object()
        students = group.students.all()
        data = [{'id': s.id, 'real_name': s.first_name, 'student_id': s.username} for s in students]
        return Response(data)


# ★★★ 核心：支持 Word 上传解析的模板管理 ★★★
class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    @action(detail=False, methods=['post'])
    def upload_docx(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj: return Response({"error": "请选择 .docx 文件"}, status=400)
        if not file_obj.name.endswith('.docx'): return Response({"error": "请上传 Word (.docx) 文件"}, status=400)

        try:
            doc = Document(file_obj)
            structure = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text: continue
                
                # 简单识别规则：Heading样式 或 以数字/冒号结尾的短句 视为标题
                if para.style.name.startswith('Heading') or (len(text) < 30 and (text[-1] in ':：' or text[0].isdigit())):
                    structure.append({"type": "header", "value": text})
                else:
                    structure.append({"type": "textarea", "label": text, "placeholder": "请输入..."})
            
            # 默认加附件上传
            structure.append({"type": "upload", "label": "截图/附件上传", "limit": 3})

            new_tpl = ReportTemplate.objects.create(
                title=file_obj.name.replace('.docx', ''),
                type='report',
                content_structure=structure,
                created_by=request.user
            )
            return Response({"id": new_tpl.id, "title": new_tpl.title, "message": "模板生成成功！"})
            
        except Exception as e:
            print(f"Docx解析错误: {e}")
            return Response({"error": "解析失败，请确保Word文档未加密"}, status=400)


class TrainingTaskViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: return TrainingTask.objects.none()
        if user.role in ['teacher', 'admin'] or user.is_superuser:
            return TrainingTask.objects.filter(teacher=user)
        if user.role == 'student':
            return TrainingTask.objects.filter(target_class__in=user.classes.all())
        return TrainingTask.objects.none()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        task = self.get_object()
        students = task.target_class.students.all()
        stats_list = []
        for student in students:
            report = StudentReport.objects.filter(task=task, student=student).first()
            stats_list.append({
                'student_id': student.id,
                'student_name': student.username,
                'student_number': student.student_id,
                'status': report.status if report else 'unsubmitted',
                'score': report.score if report else None,
                'report_id': report.id if report else None
            })
        return Response(stats_list)


class StudentReportViewSet(viewsets.ModelViewSet):
    serializer_class = StudentReportSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = StudentReport.objects.all()
        task_id = self.request.query_params.get('task')
        if task_id: queryset = queryset.filter(task_id=task_id)
        if user.role == 'teacher' or user.is_superuser: return queryset
        return queryset.filter(student=user)

    def perform_create(self, serializer):
        report = serializer.save(student=self.request.user)
        self._handle_attachments(report)
    def perform_update(self, serializer):
        report = serializer.save()
        self._handle_attachments(report)
    def _handle_attachments(self, report):
        files = self.request.FILES.getlist('new_attachments')
        for f in files: ReportAttachment.objects.create(report=report, file=f)
    @action(detail=True, methods=['delete'])
    def remove_attachment(self, request, pk=None):
        ReportAttachment.objects.filter(id=request.query_params.get('attachment_id'), report_id=pk).delete()
        return Response({'status': 'success'})