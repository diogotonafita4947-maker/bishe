from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理员后台
    path('admin/', admin.site.urls),
    
    # ★★★ 核心分发：将所有 api/ 开头的请求转发给 core 应用的 urls.py 处理 ★★★
    # 这样前端请求 http://localhost:8000/api/tasks/ 才能生效
    path('api/', include('core.urls')), 
]

# ★★★ 关键配置：允许在开发模式下通过 URL 访问上传的图片/文件 ★★★
# 如果没有这段代码，您上传的截图虽然在硬盘里，但浏览器访问 http://.../media/xxx.png 会报 404
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)