from api.views import *
from django.urls import path
from api.views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns=[   
    path('rooms/',rooms,name='rooms'),
    path('room/<int:pk>/',roomViewApi,name='room-api'),
    path('current-user/',getCurrentUser,name='current-user-api'),
    path('message/<int:pk>/',create_message,name='room-message-api'),
    path('create-room/',create_room,name='creat-room-api'),
    path('update-room/<int:pk>/',update_room,name='update-room-api'),
    path('delete-room/<int:pk>/',delete_room,name='delete-room-api'),
    path('login/',login_user,name='login-api'),
    path('logout/', logout_user,name='logout-api'),
    path('register/',register_user,name='register-api'),
    path('user/<int:pk>/',user_profile,name='user-profile-api'),
    path('activity/',activities_view,name='activity-api'),
    path('topics/',topics_view,name='topics-api'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]