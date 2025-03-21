from django.urls import path
from users.apps import UsersConfig
from users.views import LoginView, RegisterView, ProfilerView, activate, email_activated, EndRegistrationView, \
    restore_password, set_new_password, CustomLogoutView, UserListView, UsersDetailView

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfilerView.as_view(), name='profile'),
    path('activate/<str:uid>/', activate, name="activate"),
    path('email_activated', email_activated, name="email_activated"),
    path('restore_password', restore_password, name="restore_password"),
    path('restore_password/<str:uid>', set_new_password, name="set_new_password"),
    path('end_registration', EndRegistrationView.as_view(), name="end_registration"),
    path('info', UserListView.as_view(), name="user_list" ),
    path('info/<int:pk>/', UsersDetailView.as_view(), name="user_detail" )
]
