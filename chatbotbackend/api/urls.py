
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import login_token, sign_up, get_contacts, logout_token, upload_file
urlpatterns = [
    path('login/', login_token, name='login_token'),
    path('logout/', logout_token, name='logout_token'),
    path('sign_up/', sign_up, name='sign_up'),
    path('get_contacts/', get_contacts, name='get_contacts'),
    path('upload_file/', upload_file, name='upload_file'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
