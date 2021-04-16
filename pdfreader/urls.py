from pdfreader import views
from django.urls import path

urlpatterns = [
    path('', views.fake_calculate , name = "fake calculate"),
    path('accounts/login/', views.calculate , name = "calculate"),
    path('upload-csv/', views.data_upload , name = "data upload"),
    path('delete-all/', views.delete_everything , name = "delete all")
]