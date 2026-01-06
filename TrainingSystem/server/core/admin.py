from django.contrib import admin
from .models import User, ReportTemplate, TrainingTask, StudentReport, ClassGroup

admin.site.register(User)
admin.site.register(ClassGroup) # 注册班级
admin.site.register(ReportTemplate)
admin.site.register(TrainingTask)
admin.site.register(StudentReport)