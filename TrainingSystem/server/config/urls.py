from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# 务必确认这两行导入存在
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ============================================================
    # ★★★ 核心修复：登录接口必须放在第一位！ ★★★
    # ============================================================
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # ============================================================
    # 通用业务接口必须放在最后
    # 任何以 'api/' 开头的其他请求，都会进到这里
    # ============================================================
    path('api/', include('core.urls')), 
]

# 媒体文件路由
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)