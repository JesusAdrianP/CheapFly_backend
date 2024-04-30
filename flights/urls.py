from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('flights/', views.TestView.as_view() ,name='flights' )
]