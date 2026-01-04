from django.contrib import admin
from .models import User, ReportTemplate, TrainingTask, StudentReport

admin.site.register(User)
admin.site.register(ReportTemplate)
admin.site.register(TrainingTask)
admin.site.register(StudentReport)