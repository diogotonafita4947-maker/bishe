from django.core.management.base import BaseCommand
from core.models import TrainingTask, StudentReport, ReportAttachment

class Command(BaseCommand):
    help = '清除所有的任务、报告和附件，但保留用户、班级、白名单和模板'

    def handle(self, *args, **kwargs):
        self.stdout.write('正在清除业务数据...')

        # 1. 删除所有任务
        # Django 的级联删除(CASCADE)机制会自动删除关联的：
        # - StudentReport (学生报告)
        # - ReportAttachment (附件)
        # - task_context (老师填写的题目内容)
        deleted_tasks, _ = TrainingTask.objects.all().delete()
        
        # 2. (可选) 如果您想连“学生报告”也单独清空一次（防止有孤儿数据）
        deleted_reports, _ = StudentReport.objects.all().delete()

        # 3. (可选) 报告模板通常算作“资产”，建议保留。
        # 如果您连模板也想删，取消下面这行的注释：
        # from core.models import ReportTemplate
        # ReportTemplate.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'清理完成！共删除了 {deleted_tasks} 个任务。'))
        self.stdout.write(self.style.WARNING('提示：用户账号、班级、白名单及报告模板已保留。'))