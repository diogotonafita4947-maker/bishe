from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    
    # ★★★ 新增：学院和专业 (注册时自动填充) ★★★
    college = models.CharField(max_length=50, blank=True, null=True, verbose_name="学院")
    major = models.CharField(max_length=50, blank=True, null=True, verbose_name="专业")

    classes = models.ManyToManyField('ClassGroup', related_name='students', blank=True)

class StudentWhitelist(models.Model):
    name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20, unique=True)
    
    # ★★★ 新增：白名单导入字段 ★★★
    college = models.CharField(max_length=50, blank=True, null=True, verbose_name="学院")
    major = models.CharField(max_length=50, blank=True, null=True, verbose_name="专业")
    
    is_registered = models.BooleanField(default=False)

class TeacherWhitelist(models.Model):
    name = models.CharField(max_length=50)
    teacher_id = models.CharField(max_length=20, unique=True)
    is_registered = models.BooleanField(default=False)

class ClassGroup(models.Model):
    name = models.CharField(max_length=50)
    invite_code = models.CharField(max_length=10, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classes')
    created_at = models.DateTimeField(auto_now_add=True)

class ReportTemplate(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    content_structure = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True)

class TrainingTask(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_tasks')
    target_class = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='tasks')
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=100, default="计算机实训中心", verbose_name="实训地点")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    task_context = models.JSONField(default=dict, blank=True)
    max_submissions = models.IntegerField(default=1) 
    created_at = models.DateTimeField(auto_now_add=True)

class StudentReport(models.Model):
    STATUS_CHOICES = (('draft', '草稿'),('submitted', '已提交'),('graded', '已批改'),('returned', '已退回'))
    task = models.ForeignKey(TrainingTask, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    content_data = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    submit_count = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

class ReportAttachment(models.Model):
    report = models.ForeignKey(StudentReport, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)