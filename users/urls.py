from django.urls import path
from users import views
urlpatterns = [
    path('signup/', views.signup , name = "sign up"),
    path('login/', views.login , name = "login"),
    path('export/', views.export_users_csv, name='export_users_csv')
]