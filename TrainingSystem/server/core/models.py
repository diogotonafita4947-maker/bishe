from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True)
    
    # ★★★ 核心修改：改为多对多关系 (ManyToMany) ★★★
    # 允许一个学生关联多个班级，blank=True 表示可以暂时不加任何班
    classes = models.ManyToManyField('ClassGroup', related_name='students', blank=True)
    
    class Meta:
        db_table = 'user'

class StudentWhitelist(models.Model):
    name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=50) # 行政班级
    is_registered = models.BooleanField(default=False)

class TeacherWhitelist(models.Model):
    name = models.CharField(max_length=50)
    teacher_id = models.CharField(max_length=50, unique=True)
    is_registered = models.BooleanField(default=False)

class ClassGroup(models.Model):
    name = models.CharField(max_length=50)
    # 邀请码
    invite_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classes')
    created_at = models.DateTimeField(auto_now_add=True)

class ReportTemplate(models.Model):
    TYPE_CHOICES = (('daily', '日报'), ('weekly', '周报'), ('report', '实验报告'))
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content_structure = models.JSONField(default=list) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class TrainingTask(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    target_class = models.ForeignKey(ClassGroup, on_delete=models.CASCADE) # 任务还是发给某个特定班级
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reference_materials = models.ManyToManyField(ReportTemplate, related_name='tasks_as_ref', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class StudentReport(models.Model):
    STATUS_CHOICES = (('draft', '草稿'), ('submitted', '已提交'), ('graded', '已批改'))
    task = models.ForeignKey(TrainingTask, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    content_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

class ReportAttachment(models.Model):
    report = models.ForeignKey(StudentReport, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)