from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='market_regime_classifier_index'),
    path('live-data/', views.live_data, name='market_regime_classifier_live_data'),
]