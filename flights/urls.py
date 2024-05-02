from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('flights/', views.GetFlightsView.as_view() ,name='flights' )
]