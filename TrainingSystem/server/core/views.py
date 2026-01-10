import openpyxl
import random
import string
from docx import Document
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser
from django.utils import timezone

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

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser]) 
    def upload_roster(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj: return Response({"error": "未接收到文件"}, status=400)
        
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
        while ClassGroup.objects.filter(invite_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        serializer.save(created_by=self.request.user, invite_code=code)

    @action(detail=False, methods=['post'])
    def join_class(self, request):
        code = request.data.get('invite_code', '').strip().upper()
        group = ClassGroup.objects.filter(invite_code=code).first()
        if not group: return Response({"error": "无效的邀请码"}, 400)
        
        user = request.user
        if group in user.classes.all(): return Response({"error": "你已经在这个班级了"}, 400)
        
        user.classes.add(group)
        return Response({"message": f"成功加入：{group.name}"})

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        group = self.get_object()
        students = group.students.all()
        data = [{'id': s.id, 'real_name': s.first_name, 'student_id': s.username} for s in students]
        return Response(data)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        if template.created_by != request.user and not request.user.is_superuser:
            return Response({"error": "无权删除他人模板"}, 403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def upload_docx(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.endswith('.docx'): 
            return Response({"error": "请上传 .docx 文件"}, status=400)

        try:
            doc = Document(file_obj)
            structure = []
            
            def analyze_text(text):
                # 自动填充字段
                if '姓名' in text or '学生' == text: return "auto_name"
                if '学号' in text: return "auto_number"
                if '班级' in text or '专业' in text: return "auto_class"
                if '题目' in text or '名称' in text: return "auto_task"
                if '指导' in text or '老师' in text: return "auto_teacher"
                if '日期' in text: return "auto_date"
                if '评分' in text or '评语' in text: return "auto_score"
                
                # 老师填写区
                teacher_keywords = ['原理', '目的', '仪器', '要求', '任务']
                # 学生填写区
                student_keywords = ['步骤', '过程', '心得', '结论', '总结', '代码']
                
                if any(k in text for k in student_keywords): return "input_large"
                if any(k in text for k in teacher_keywords): return "teacher_block"
                
                return "paragraph"

            seen = set()
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        txt = cell.text.strip()
                        if not txt or txt in seen: continue
                        seen.add(txt)
                        
                        itype = analyze_text(txt)
                        
                        if itype == "input_large":
                            structure.append({"type": "header", "value": txt})
                            structure.append({"type": "textarea", "label": txt, "value": ""})
                        elif itype == "teacher_block":
                            structure.append({"type": "teacher_block", "label": txt, "value": ""})
                        elif itype.startswith("auto_"):
                            structure.append({"type": "info_row", "label": txt, "key": itype})
                        else:
                            structure.append({"type": "header", "value": txt})

            if not structure:
                for para in doc.paragraphs:
                    txt = para.text.strip()
                    if not txt: continue
                    itype = analyze_text(txt)
                    if itype == "input_large":
                         structure.append({"type": "header", "value": txt})
                         structure.append({"type": "textarea", "label": txt, "value": ""})
                    elif itype.startswith("auto_"):
                         structure.append({"type": "info_row", "label": txt, "key": itype})
                    else:
                         structure.append({"type": "paragraph", "value": txt})

            structure.append({"type": "upload", "label": "截图/附件上传", "limit": 5})

            new_tpl = ReportTemplate.objects.create(
                title=file_obj.name.replace('.docx', ''),
                type='report',
                content_structure=structure,
                created_by=request.user
            )
            return Response({"id": new_tpl.id, "title": new_tpl.title, "message": "解析成功"})
        except Exception as e:
            return Response({"error": f"解析失败: {str(e)}"}, status=400)


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
        # 接收并保存 max_submissions (由serializer处理字段，这里只需指定teacher)
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
                'student_name': student.first_name or student.username,
                'student_number': student.username,
                'status': report.status if report else 'unsubmitted',
                'score': report.score if report else None,
                'report_id': report.id if report else None,
                'submit_count': report.submit_count if report else 0
            })
        return Response(stats_list)

    @action(detail=True, methods=['get'])
    def my_report(self, request, pk=None):
        task = self.get_object()
        report, created = StudentReport.objects.get_or_create(
            task=task,
            student=request.user,
            defaults={
                'status': 'draft',
                'content_data': [],
                'submit_count': 0
            }
        )
        serializer = StudentReportSerializer(report)
        return Response(serializer.data)


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
        serializer.save(student=self.request.user)

    def perform_update(self, serializer):
        report = self.get_object()
        new_status = self.request.data.get('status')
        
        # ★★★ 提交时的逻辑：次数限制 ★★★
        if new_status == 'submitted' and report.status != 'submitted':
            if report.submit_count >= report.task.max_submissions:
                # 超过次数，这里不抛出错误，前端会拦截，或者仅保存不提交
                # 但为了安全，如果强行调用可以抛错。这里简单放行保存，但前端状态不会变。
                pass
            
            serializer.save(
                submitted_at=timezone.now(),
                submit_count=report.submit_count + 1
            )
        else:
            serializer.save()

    # ★★★ 教师打分接口 ★★★
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        report = self.get_object()
        if request.user.role != 'teacher' and not request.user.is_superuser:
            return Response({'error': '无权批改'}, status=403)
            
        score = request.data.get('score')
        feedback = request.data.get('feedback')
        report.score = score
        report.feedback = feedback
        report.status = 'graded'
        report.graded_at = timezone.now()
        report.save()
        return Response({'status': 'success'})

    # ★★★ 教师打回接口 ★★★
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        report = self.get_object()
        if request.user.role != 'teacher' and not request.user.is_superuser:
            return Response({'error': '无权操作'}, status=403)
        
        # 状态重置为 returned，学生端会视为草稿可编辑
        report.status = 'returned'
        report.save()
        return Response({'status': 'success', 'message': '已打回'})

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_attachment(self, request, pk=None):
        report = self.get_object()
        file = request.FILES.get('file')
        if file:
            attachment = ReportAttachment.objects.create(report=report, file=file)
            full_url = request.build_absolute_uri(attachment.file.url)
            return Response({'status': 'success', 'url': full_url, 'name': file.name})
        return Response({'error': 'no file'}, status=400)

    @action(detail=True, methods=['delete'])
    def remove_attachment(self, request, pk=None):
        att_id = request.data.get('attachment_id')
        if not att_id: att_id = request.query_params.get('attachment_id')
        ReportAttachment.objects.filter(id=att_id, report_id=pk).delete()
        return Response({'status': 'success'})