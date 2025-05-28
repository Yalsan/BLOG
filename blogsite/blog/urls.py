from django.urls import path
from . import views

urlpatterns = [
    path('', views.Homepage, name='homepage'),
    path('create/',views.post_create, name='create'),
    path('<int:id>/delete/', views.post_delete, name='delete'),
    path('category/<str:cat_name>/', views.categoryview, name='category'),
    path("signin",views.sign_in,name="signin"),
    path("signup",views.sign_up,name="signup"),
    path('logout/', views.log_out, name='logout'),
    path('update/<int:id>/', views.update, name='updatee'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('like/<int:article_id>/', views.like_article, name='like_article'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path("contact",views.contact_us,name="contact"),

]

   



