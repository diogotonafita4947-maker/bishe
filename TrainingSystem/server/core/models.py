from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. 班级模型
class ClassGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name="班级名称")
    invite_code = models.CharField(max_length=6, unique=True, verbose_name="加入邀请码")
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_classes', verbose_name="创建教师")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "班级管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.invite_code})"

# 2. 用户表
class User(AbstractUser):
    ROLE_CHOICES = (('student', '学生'), ('teacher', '教师'), ('admin', '管理员'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name="用户角色")
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="学号/工号")
    phone = models.CharField(max_length=20, blank=True, verbose_name="手机号码")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name="所属班级")

    class Meta:
        verbose_name = "系统用户"

# 3. 文档/模板表
class ReportTemplate(models.Model):
    TYPE_CHOICES = (
        ('material', '📚 教学材料'),
        ('guide', '🧭 实训指导书'),
        ('plan', '📋 实训教案'),
        ('report', '📝 实训报告'),
    )
    
    title = models.CharField(max_length=100, verbose_name="文档名称")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='report', verbose_name="文档类型")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    content_structure = models.JSONField(default=list, verbose_name="文档结构(JSON)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "教学资源库"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"

# 4. 实训任务表
class TrainingTask(models.Model):
    STATUS_CHOICES = (('draft', '草稿'), ('published', '进行中'), ('finished', '已结束'))
    
    title = models.CharField(max_length=100, verbose_name="任务标题")
    description = models.TextField(blank=True, verbose_name="任务备注")
    
    # 存老师填写的【实验原理、目的、器材、要求、地点】
    task_details = models.JSONField(default=dict, verbose_name="实训详情数据")

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_tasks', verbose_name="发布教师")
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT, related_name='tasks_as_homework', verbose_name="作业模板")
    reference_materials = models.ManyToManyField(ReportTemplate, blank=True, related_name='tasks_as_reference', verbose_name="关联参考资料")
    target_class = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='tasks', verbose_name="目标班级")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="截止时间")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="当前状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "实训任务"

# 5. 学生报告表
class StudentReport(models.Model):
    STATUS_CHOICES = (('draft', '草稿'), ('submitted', '已提交'), ('returned', '被退回'), ('graded', '已评分'))
    
    task = models.ForeignKey(TrainingTask, on_delete=models.CASCADE, verbose_name="所属任务")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_reports', verbose_name="学生姓名")
    content_data = models.JSONField(default=dict, verbose_name="报告内容(JSON)")
    
    # 旧的单附件字段，保留以兼容旧数据
    attachment = models.FileField(upload_to='reports/attachments/', blank=True, null=True, verbose_name="附件(旧)")
    
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="最终成绩")
    teacher_comment = models.TextField(blank=True, verbose_name="教师评语")
    ai_suggestion = models.TextField(blank=True, null=True, verbose_name="AI评分建议")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ('task', 'student')
        verbose_name = "学生报告"

# 6. ★★★ 新增：报告附件表 (支持无限上传) ★★★
class ReportAttachment(models.Model):
    report = models.ForeignKey(StudentReport, on_delete=models.CASCADE, related_name='attachments', verbose_name="所属报告")
    file = models.FileField(upload_to='reports/attachments/', verbose_name="文件")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")

    def __str__(self):
        return f"附件: {self.file.name}"