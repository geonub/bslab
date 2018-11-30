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
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    #가입
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', TemplateView.as_view(template_name='registration/signup_select.html'),
         name='signup_select'),
    path('accounts/signup/student', asap_view.CreateStudentView.as_view(),name='signup_student'),
    path('accounts/signup/prof', asap_view.CreateProfView.as_view(),name='signup_prof'),
    
    #인증
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            asap_view.UserActivateView.as_view(), name='activate'),

    #교강사
    path('research/create', asap_view.create_view_research, name='create_research'),
    re_path(r'^research/modify/(?P<pk>[0-9]*)/$',
                asap_view.modify_research, name='modify_research'),
    re_path(r'^research/delete/(?P<pk>[0-9]*)/$',
                asap_view.delete_research, name='delete_research'),
    re_path(r'^research/(?P<pk>[0-9]*)/$',
            asap_view.create_unit, name='create_unit'),
    re_path(r'^research/(?P<rpk>[0-9]*)/modify/(?P<upk>[0-9]*)/$',
            asap_view.modify_unit, name='modify_unit'),
    re_path(r'^research/(?P<rpk>[0-9]*)/delete/(?P<upk>[0-9]*)/$',
            asap_view.delete_unit, name='delete_unit'),

    path('prof/manage', asap_view.list_manage_unit, name='list_manage_unit'),
    re_path(r'^prof/manage/(?P<pk>[0-9]*)/$',
            asap_view.manage_unit, name='manage_unit'),

    #학생 메뉴
    path('research/enroll', asap_view.enroll_view_unit, name='enroll_page'),
    re_path(r'^research/enroll/(?P<pk>[0-9]*)/$',
            asap_view.enroll_unit, name='enroll_unit'),
    re_path(r'^research/cancel/(?P<pk>[0-9]*)/$',
            asap_view.cancel_unit, name='cancel_unit'),
    path('student/myresearch', asap_view.my_research_student, name='my_research_student'),

    #실험 조회 및 정보
    path('research/all', asap_view.AllResearchListView.as_view(), name='all_research'),
    re_path(r'^research/info/(?P<pk>[0-9]*)/$',
            asap_view.research_info, name='research_info'),

    #개인 설정 메뉴
    path('mypage/', asap_view.my_page, name='my_page'),
    path('mypage/changepassword/', asap_view.change_password, name='change_password'),

    #단순 출력
    path('done/', TemplateView.as_view(template_name='done.html'), name='done'),
    path('warning/', TemplateView.as_view(template_name='warning.html'), name='warning'),
    path('intro/', TemplateView.as_view(template_name='intro.html'), name='intro'),
    path('accounts/signup/done', TemplateView.as_view(template_name='registration/signup_done.html'), name='create_user_done'),

]


