from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import User, Student, Prof, Research, Unit, Record
from django.db.models import Count
from .forms import StudentSignUpForm, ProfSignUpForm, CreateResearchForm, CreateUnitForm, RecordScoreFormSet
from .forms import ModifyProfForm, ModifyStudentForm

import logging

# <------------------------------------가입/인증 View------------------------------------>

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

# <------------------------------------강사 View------------------------------------>


def create_view_research(request):
    research_list = Research.objects.filter(prof_obj=Prof.objects.get(user=request.user))

    if request.method == "POST":
        form = CreateResearchForm(request.POST)
        if form.is_valid():
            research_form = form.save(commit = False)
            research_form.prof_obj = Prof.objects.get(user=request.user)
            research_form.save()
            messages.success(request, '성공적으로 등록되었습니다!')
            return render(request, 'create_view_research.html', {'research_form': form, 'research_list': research_list})
    else:
        form = CreateResearchForm()
        return render(request, 'create_view_research.html', {'research_form': form, 'research_list': research_list})

def modify_research(request, pk):
    target = Research.objects.get(pk=pk)

    if target.prof_obj != Prof.objects.get(user=request.user):
        return redirect('warning')

    if request.method == "POST":
        form = CreateResearchForm(request.POST, instance=target)
        if form.is_valid():
             form.save()
             messages.success(request, '성공적으로 수정되었습니다!')
             return redirect('create_research')
    else:
        research_list = Research.objects.filter(prof_obj=Prof.objects.get(user=request.user))
        form = CreateResearchForm(instance = target)
        return render(request, 'modify_research.html', {'research_form': form, 'research_list': research_list, 'target': target})

def delete_research(request, pk):
    target = Research.objects.get(pk=pk)

    if target.prof_obj == Prof.objects.get(user=request.user):
        target.delete()
        messages.success(request, '성공적으로 삭제되었습니다!')
        return redirect('create_research')
    else:
        return redirect('warning')
    

def create_unit(request, pk):
    research_obj = Research.objects.get(pk=pk)

    if research_obj.prof_obj != Prof.objects.get(user=request.user):
        return redirect('warning')

    unit_list = Unit.objects.filter(research_obj=Research.objects.get(pk=pk))

    if request.method == "POST":
        form = CreateUnitForm(request.POST)
        if form.is_valid():
            unit_form = form.save(commit=False)
            unit_form.research_obj = Research.objects.get(pk=pk)
            unit_form.save()
            messages.success(request, '성공적으로 등록되었습니다!')
            return render(request, 'create_unit.html', {'research_obj': research_obj, 'unit_form': form, 'unit_list': unit_list, 'rpk': pk})
    else:
        form = CreateUnitForm()
        return render(request, 'create_unit.html', {'research_obj': research_obj, 'unit_form': form, 'unit_list': unit_list, 'rpk': pk})


def modify_unit(request, rpk, upk):
    research_obj = Research.objects.get(pk=rpk)
    target = Unit.objects.get(pk=upk)

    if research_obj.prof_obj != Prof.objects.get(user=request.user):
        return redirect('warning')

    if request.method == "POST":
        form = CreateUnitForm(request.POST, instance=target)
        if form.is_valid():
             form.save()
             messages.success(request, '성공적으로 수정되었습니다!')
             return redirect('create_unit', pk=rpk)
    else:
        unit_list = Unit.objects.filter(research_obj=Research.objects.get(pk=rpk))
        form = CreateUnitForm(instance=target)
        return render(request, 'modify_unit.html', {'research_obj': research_obj, 'unit_form': form, 'unit_list': unit_list, 'target': target})


def delete_unit(request, rpk, upk):
    target = Unit.objects.get(pk=upk)

    if target.research_obj.prof_obj == Prof.objects.get(user=request.user):
        target.delete()
        messages.success(request, '성공적으로 삭제되었습니다!')
        return redirect('create_unit', pk=rpk)
    else:
        return redirect('warning')


def list_manage_unit(request):
    objects = Research.objects.filter(prof_obj=Prof.objects.get(user=request.user))
    unit_list = Unit.objects.filter(research_obj__in=objects)
    return render(request, 'list_manage_unit.html', {'unit_list': unit_list, })

def manage_unit(request, pk):
    target_unit = Unit.objects.get(pk=pk)

    # 타인 강의 접근 차단
    if not target_unit.research_obj.prof_obj == Prof.objects.get(user=request.user):
        return redirect('warning')

    target_list = Record.objects.filter(unit_obj=target_unit)
    if request.method == "POST":
        formset = RecordScoreFormSet(request.POST, queryset=target_list,)
        if formset.is_valid():
            for fs in formset:
                if fs.is_valid():
                    fs.save()
            messages.success(request, '성공적으로 입력되었습니다!')
            return redirect('manage_unit',pk)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        formset = RecordScoreFormSet(queryset=target_list,)
        zip_form = zip(target_list, formset)
        return render(request, 'manage_unit.html', {'pk': pk, 'form': formset, 'zip_form': zip_form, })

# <------------------------------------학생 View------------------------------------>


def enroll_view_unit(request):
    all_units = Unit.objects.all()
    my_records = Record.objects.filter(student_obj=Student.objects.get(user=request.user))
    my_researchs = Research.objects.filter(unit__record__in = my_records)
    return render(request, 'enroll_view_unit.html', {'all_units': all_units, 'my_records': my_records, 'my_researchs': my_researchs.values_list('research_name', flat=True)})

def enroll_unit(request, pk):
    target_unit = Unit.objects.get(pk=pk)
    me = Student.objects.get(user = request.user)

    try: #신청 여부 검사
        Record.objects.get(student_obj=me, unit_obj=target_unit)
        messages.error(request, '이미 신청완료한 실험입니다!')
        return redirect('enroll_page')

    except Record.DoesNotExist:
        if target_unit.current_number >= target_unit.max_number:  # 수강 정원 검사
            messages.error(request, '정원 초과입니다. 다른 실험을 선택하여 주시기 바랍니다.')
            return redirect('enroll_page')

        record = Record.objects.create(student_obj=me, unit_obj=target_unit)
        record.save()
        messages.success(request, '실험신청을 성공하였습니다!')
        target_unit.current_number += 1
        target_unit.save()
        return redirect('enroll_page')

def cancel_unit(request,pk):
    target_record = Record.objects.get(pk=pk)
    if target_record.student_obj == Student.objects.get(user=request.user):
        target_record.unit_obj.current_number -= 1
        target_record.unit_obj.save()
        target_record.delete()
        messages.success(request, '신청 취소되었습니다.')
        return redirect('enroll_page')
    else:
        return redirect('warning')

def my_research_student(request):
    my_researches = Record.objects.filter(student_obj=Student.objects.get(user=request.user))
    return render(request, 'my_research_student.html',{'my_researches': my_researches,})

# <------------------------------------실험 조회/정보 View------------------------------------>


class AllResearchListView(ListView):
    template_name = 'all_research.html'
    context_object_name='all_researches'

    #검색창 
    def get_queryset(self):
        q = self.request.GET.get('q', '')
        q_option = self.request.GET.get('q_option')
        if q:
            if q_option == "prof":
                return Research.objects.filter(prof_obj__user__name__icontains=q)
            else:
                filter_dict = {q_option+'__icontains': q}
                return Research.objects.filter(**filter_dict)
        else:
            return Research.objects.filter()


def research_info(request, pk):
    research_obj = Research.objects.get(pk=pk)
    unit_list = Unit.objects.filter(research_obj=research_obj)
    return render(request, 'research_info.html', {'research_obj': research_obj, 'unit_list': unit_list,})

# <------------------------------------개인 설정 메뉴 View------------------------------------>


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
