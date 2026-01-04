from django.db import models
from django.contrib.auth.models import AbstractUser

# =========================================================
# 1. 用户表设计
# 继承 Django 自带的 AbstractUser，方便使用系统自带的登录功能
# =========================================================
class User(AbstractUser):
    # 定义用户角色选项：数据库存英文(key)，界面显示中文(value)
    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    )
    
    # 扩展字段
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name="用户角色")
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="学号/工号")
    college = models.CharField(max_length=50, blank=True, verbose_name="所属学院")
    major_class = models.CharField(max_length=50, blank=True, verbose_name="专业班级")
    phone = models.CharField(max_length=20, blank=True, verbose_name="手机号码")

    class Meta:
        verbose_name = "系统用户"
        verbose_name_plural = verbose_name # 复数形式也显示为中文

    def __str__(self):
        # 在后台显示时，显示格式为：张三 (学生)
        return f"{self.username} ({self.get_role_display()})"


# =========================================================
# 2. 报告模板表设计
# 核心功能：存储 JSON 格式的表单结构，实现“在线编辑”的底座
# =========================================================
class ReportTemplate(models.Model):
    TYPE_CHOICES = (
        ('guide', '实训指导书'),
        ('plan', '实训教案'),
        ('report', '实训报告'),
    )
    
    title = models.CharField(max_length=100, verbose_name="模板名称")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='report', verbose_name="模板类型")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建人")
    
    # 重点：这里存储 JSON 数据，例如 [{"type": "input", "label": "实训目的"}]
    content_structure = models.JSONField(default=list, verbose_name="模板结构数据(JSON)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "文档模板"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# =========================================================
# 3. 实训任务表设计
# 老师发布的具体作业，关联了一个模板
# =========================================================
class TrainingTask(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '进行中'),
        ('finished', '已结束'),
    )
    
    title = models.CharField(max_length=100, verbose_name="任务标题")
    description = models.TextField(blank=True, verbose_name="任务详细说明")
    
    # related_name 方便反向查询，例如：查询该老师发布的所有任务
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_tasks', verbose_name="发布教师")
    
    # 必须关联一个模板，学生根据这个模板写作业
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT, verbose_name="所选模板")
    
    target_class = models.CharField(max_length=50, verbose_name="面向班级") 
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="截止时间")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="当前状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "实训任务管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# =========================================================
# 4. 学生报告表设计
# 存储学生填写的内容、成绩和老师评语
# =========================================================
class StudentReport(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿(未提交)'),
        ('submitted', '已提交(待批改)'),
        ('returned', '被退回(需修改)'),
        ('graded', '已评分(流程结束)'),
    )
    
    task = models.ForeignKey(TrainingTask, on_delete=models.CASCADE, verbose_name="所属实训任务")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_reports', verbose_name="学生姓名")
    
    # 重点：存储学生填写的具体内容，是 JSON 格式
    content_data = models.JSONField(default=dict, verbose_name="报告内容数据(JSON)")
    
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="最终成绩")
    teacher_comment = models.TextField(blank=True, verbose_name="教师评语")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="报告状态")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        # 联合唯一索引：确保一个任务，一个学生，只能有一份报告
        unique_together = ('task', 'student')
        verbose_name = "学生提交的报告"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"