from django.urls import path
from . import views
from .views import like_comment, dislike_comment

urlpatterns = [
    path('SignIn/', views.SignIn, name='SignIn'),
    path('SignUp/', views.SignUp, name='SignUp'),
    path('LogOut/', views.LogOut, name='LogOut'),
    path('account/<int:pk>/', views.account, name='account'),
    path('settings/', views.settings, name='settings'),
    path('', views.threads, name='threads'),
    path('post/create/', views.created, name='created'),
    path('post/<int:pk>/', views.summary, name='summary'),
    path('post/<int:pk>/update/', views.updated, name='updated'),
    path('post/<int:pk>/delete/', views.delete, name='delete'),
    path('post/<str:pk>/comment/', views.Commented, name='Commented'),
    path('comment/<int:comment_id>/delete/', views.delete_comment,
         name='delete_comment'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/dislike/', views.dislike_post, name='dislike_post'),
    path('like-comment/<int:pk>/', like_comment, name='like_comment'),
    path('dislike-comment/<int:pk>/', dislike_comment, name='dislike_comment'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('verify-otp/', views.VerifyOTP, name='VerifyOTP'),
]
