import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ReportTemplate, User

def create_standard_template():
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ 请先创建管理员账号")
        return

    # ★★★ 修改这里：只保留学生需要填写的内容 ★★★
    # 老师填写的内容已经移到 Task 表里了，模板里不需要了
    student_structure = [
        {"type": "header", "value": "四、实验(训)步骤或过程"},
        {"type": "textarea", "label": "实验步骤/过程内容", "placeholder": "请详细记录实验步骤、代码实现或操作过程..."},
        
        {"type": "header", "value": "五、实验(训)结论与心得"},
        {"type": "textarea", "label": "结论与心得", "placeholder": "不少于500字..."}
    ]

    # 创建或更新模板
    template, created = ReportTemplate.objects.get_or_create(
        title="标准实验报告模板 (学生填写版)",
        defaults={
            "type": "report",
            "created_by": admin_user,
            "content_structure": student_structure
        }
    )

    if not created:
        template.content_structure = student_structure
        template.save()
        print("🔄 已更新模板结构：只包含步骤和心得")
    else:
        print("✅ 成功创建新模板")

if __name__ == '__main__':
    create_standard_template()