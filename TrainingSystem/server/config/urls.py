from django.contrib import admin
from django.urls import path, include
# 引入登录认证的模块
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ★ 关键：把 api/ 开头的请求，转交给 core 部门处理
    path('api/', include('core.urls')), 
    
    # 登录接口
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]