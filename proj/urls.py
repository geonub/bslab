"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from asap import views as asap_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', asap_view.IndexView.as_view(), name='index'),

    #가입
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', asap_view.SignupSelectView.as_view(),name='signup_select'),
    path('accounts/signup/student', asap_view.CreateStudentView.as_view(),name='signup_student'),
    path('accounts/signup/prof', asap_view.CreateProfView.as_view(),name='signup_prof'),
    path('accounts/signup/done', asap_view.RegisteredView.as_view(), name='create_user_done'),
    
    #인증
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            asap_view.UserActivateView.as_view(), name='activate'),

    #교강사
    path('research/create', asap_view.create_and_view_my_research, name='create_research'),
    re_path(r'^research/modify/(?P<pk>[0-9]*)/$',
                asap_view.modify_my_research, name='modify_research'),
    re_path(r'^research/delete/(?P<pk>[0-9]*)/$',
                asap_view.delete_my_research, name='delete_research'),
    path('prof/myresearch', asap_view.my_research_prof, name='my_research_prof'),
    re_path(r'^prof/myresearch/(?P<pk>[0-9]*)/$',
            asap_view.manage_my_research, name='manage_my_research'),


    #기타
    path('warning', asap_view.WarningView.as_view(), name='warning'),


    #학생 메뉴
    path('research/enroll', asap_view.enroll_and_view_my_research, name='enroll_page'),
    re_path(r'^research/enroll/(?P<pk>[0-9]*)/$',
            asap_view.enroll_research, name='enroll_research'),
    re_path(r'^research/cancel/(?P<pk>[0-9]*)/$',
            asap_view.cancel_research, name='cancel_research'),
    path('student/myresearch', asap_view.my_research_student, name='my_research_student'),

    #전체메뉴
    path('research/all', asap_view.AllResearchListView.as_view(), name='all_research'),
    path('mypage/', asap_view.my_page, name='my_page'),
    path('mypage/changepassword/', asap_view.change_password, name='change_password'),

    #기타
    path('done/', asap_view.DoneView.as_view(), name='done'),

    #소개
    path('intro/', asap_view.IntroView.as_view(), name='intro'),

    #개별실험소개
    path('researchinfo/', asap_view.ResearchInfoView.as_view(), name='research_info'),


]


