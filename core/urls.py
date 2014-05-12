from core import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^recipe-names$', views.recipeNames, name='recipeNames'),
    url(r'^recommendRecipes', views.recommendRecipes, name='recommendRecipes'),
)

