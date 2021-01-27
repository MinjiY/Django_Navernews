from django.urls import path
from django.conf.urls import url

from news import views

app_name='news'
urlpatterns = [
    path('',views.news_list, name='news_list'),
    path('<int:sid1>/<int:sid2>', views.news_detail, name='news_detail'),
    path('<str:sports>/', views.news_sports, name='news_sports'),

]
