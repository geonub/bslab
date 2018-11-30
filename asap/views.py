from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import User, Student, Prof, Research, Record
from django.db.models import Count
from .forms import StudentSignUpForm, ProfSignUpForm, CreateResearchForm, RecordScoreFormSet
from .forms import ModifyProfForm, ModifyStudentForm
from django.core.management.base import BaseCommand
from django.core.cache import cache

import logging

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cleared cache\n')

class UserActivateView(TemplateView):
    logger = logging.getLogger(__name__)
    template_name = 'registration/user_activate_email_done.html'

    def get(self, request, *args, **kwargs):
        self.logger.debug('UserActivateView.get()')

        uid = force_text(urlsafe_base64_decode(self.kwargs['uidb64']))
        token = self.kwargs['token']

        self.logger.debug('uid: %s, token: %s' % (uid, token))

        try:
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.logger.warning('User %s not found' % uid)
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()
            self.logger.info('User %s(pk=%s) has been activated.' % (user, user.pk))

        return super(UserActivateView, self).get(request, *args, **kwargs)

class IndexView(TemplateView):
    template_name = 'index.html'

class IntroView(TemplateView):
    template_name = 'intro.html'

class WarningView(TemplateView):
    template_name = 'warning.html'

class SignupSelectView(TemplateView):
    template_name = 'registration/signup_select.html'

class CreateStudentView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_student.html'
    success_url = reverse_lazy('create_user_done')

class CreateProfView(CreateView):
    model = User
    form_class = ProfSignUpForm
    template_name = 'registration/signup_prof.html'
    success_url = reverse_lazy('create_user_done')

class RegisteredView(TemplateView):
    template_name = 'registration/signup_done.html'

def create_and_view_my_research(request):
    my_researches = Research.objects.filter(prof = Prof.objects.get(user = request.user))
    if request.method == "POST":
        form = CreateResearchForm(request.POST)
        if form.is_valid():
            research_form = form.save(commit = False)
            research_form.prof = Prof.objects.get(user = request.user)
            research_form.save()
            messages.success(request, '성공적으로 등록되었습니다!')
            return render(request, 'create_and_view_my_research.html',{'create_research': form, 'my_researches': my_researches})
    else:
        form = CreateResearchForm()
        return render(request, 'create_and_view_my_research.html',{'create_research': form, 'my_researches': my_researches})

def modify_my_research(request, pk):
    target = Research.objects.get(pk=pk)

    if request.method == "POST":
        form = CreateResearchForm(request.POST, instance=target)
        if form.is_valid():
             form.save()
             messages.success(request, '성공적으로 수정되었습니다!')
             return redirect('create_research')
    else:
        if target.prof == Prof.objects.get(user = request.user):
            my_researches = Research.objects.filter(prof = Prof.objects.get(user=request.user))
            form = CreateResearchForm(instance = target)
            return render(request, 'modify_my_research.html',{'modify_research': form, 'my_researches': my_researches, 'target': target})
        else:
            return redirect('warning')        

def delete_my_research(request, pk):
    target = Research.objects.get(pk=pk)
    if target.prof == Prof.objects.get(user = request.user):
        target.delete()
        messages.success(request, '성공적으로 삭제되었습니다!')
        return redirect('create_research')
    else:
        return redirect('warning')
    
def my_research_prof(request):
    my_researches = Research.objects.filter(prof = Prof.objects.get(user = request.user))
    return render(request, 'my_research_prof.html',{'my_researches': my_researches, })

def manage_my_research(request, pk):
    target_research = Research.objects.get(pk=pk)

    # 타인 강의 접근 방어
    if not target_research.prof == Prof.objects.get(user = request.user):
        return redirect('warning')

    target_list = Record.objects.filter(title=target_research)
    if request.method == "POST":
        formset = RecordScoreFormSet(request.POST, queryset=target_list,)
        if formset.is_valid():
            for fs in formset:
                if fs.is_valid():
                    fs.save()
            messages.success(request, '성공적으로 입력되었습니다!')
            return redirect('manage_my_research',pk)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        formset = RecordScoreFormSet(queryset=target_list,)
        zip_form = zip(target_list, formset)
        return render(request, 'manage_my_research.html',{'pk': pk, 'form': formset, 'zip_form': zip_form,})

#학생
def enroll_and_view_my_research(request):
    all_researches = Research.objects.all()
    my_records = Record.objects.filter(student=Student.objects.get(user=request.user))    
    my_researches = Research.objects.filter(record__in = my_records)
    return render(request, 'enroll_and_view_my_research.html',{'all_researches': all_researches, 'my_records': my_records, 'research_list': my_researches.values_list('title', flat=True)})

def enroll_research(request, pk):
    target_research = Research.objects.get(pk=pk)
    me = Student.objects.get(user = request.user)

    try:
        Record.objects.get(student=me, title=target_research)
        messages.error(request, '이미 신청완료한 실험입니다!')
        return redirect('enroll_page')

    except Record.DoesNotExist:
        if target_research.current_number >= target_research.max_number:
            messages.error(request, '정원 초과입니다. 다른 실험을 선택하여 주시기 바랍니다.')
            return redirect('enroll_page')

        record = Record.objects.create(student=me, title=target_research)
        record.save()
        messages.success(request, '실험신청을 성공하였습니다!')
        target_research.current_number += 1
        target_research.save()
        return redirect('enroll_page')

def cancel_research(request,pk):
    target_research = Record.objects.get(pk=pk)
    if target_research.student == Student.objects.get(user = request.user):
        target_research.title.current_number -=1
        target_research.title.save()
        target_research.delete()
        messages.success(request, '신청 취소되었습니다.')
        return redirect('enroll_page')
    else:
        return redirect('warning')

def my_research_student(request):
    my_researches = Record.objects.filter(student=Student.objects.get(user=request.user))
    return render(request, 'my_research_student.html',{'my_researches': my_researches,})

class ResearchInfoView(TemplateView):
    template_name = 'research_info.html'

class AllResearchListView(ListView):
    template_name = 'all_research.html'
    context_object_name='all_researches'

    #검색창 
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        q_option = self.request.GET.get('q_option')
        if q:
            if q_option == "prof":
                return Research.objects.filter(prof__user__name__icontains=q)
            else:
                filter_dict = {q_option+'__icontains': q}
                return Research.objects.filter(**filter_dict)
        else:
            return Research.objects.filter()

class DoneView(TemplateView):
    template_name = 'done.html'

# 전체메뉴
def my_page(request):
    if request.user.is_student:
        target = Student.objects.get(user=request.user)
        form_type = ModifyStudentForm
    elif request.user.is_prof:
        target = Prof.objects.get(user=request.user)
        form_type = ModifyProfForm
    else:
        target_user = request.user
        return render(request, 'my_page.html',{'user_profile': target_user})

    target_user = target.user

    if request.method == "POST":
        form = form_type(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, '정보가 성공적으로 변경되었습니다.')
            return redirect('my_page')
        else:
            messages.error(request, '에러가 발생하였습니다.')
    else:
        form = form_type(instance=target)
        return render(request, 'my_page.html',{'form': form, 'user_profile': target_user})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('done')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})


# Create your views here.
