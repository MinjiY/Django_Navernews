from django.urls import path
from django.conf.urls import url

from news import views

app_name='news'
urlpatterns = [
    path('',views.news_list, name='news_list'),
    path('news/search/', views.news_search, name='news_search'),
    path('news/<int:sid1>/<int:sid2>/', views.news_detail, name='news_detail'),
    path('news/<str:sports>/', views.news_sports, name='news_sports'),
]
