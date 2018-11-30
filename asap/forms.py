from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, Prof, Research, Record, Unit

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage

from bootstrap_datepicker_plus import DateTimePickerInput

class StudentSignUpForm(UserCreationForm):

    student_number = forms.CharField(max_length=10)
    major = forms.CharField(max_length=10)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "password1", "password2", "name",
                  "sex",)

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.is_active = False #False 후에 바꿀예정
            user.is_student = True
            user.save()
            student = Student.objects.create(user=user)
            student.student_number = self.cleaned_data.get('student_number')
            student.major = self.cleaned_data.get('major')
            student.save()

            current_site = Site.objects.get_current()
            current_site.domain = '52.78.163.167'
            subject = '실험관리시스템에 가입해주셔서 감사합니다. 이메일을 인증 절차를 완료해주세요.'
            message = render_to_string('registration/user_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': PasswordResetTokenGenerator().make_token(user),
            })
            email = EmailMessage(subject, message, to=[user.email])
            email.send()
        return user

class ProfSignUpForm(UserCreationForm):

    prof_number = forms.CharField(max_length=10)
    major = forms.CharField(max_length=10)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "password1", "password2", "name",
                  "sex",)

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.is_active = False
            user.is_prof = True
            user.save()
            prof = Prof.objects.create(user=user)
            prof.prof_number = self.cleaned_data.get('prof_number')
            prof.major = self.cleaned_data.get('major')
            prof.save()

        return user

class CreateResearchForm(forms.ModelForm):
    class Meta():
        model = Research
        fields = ('research_number', 'research_name', 'year', 'semester', 'description',)


class CreateUnitForm(forms.ModelForm):
    class Meta():
        model = Unit
        fields = ('place', 'date', 'period', 'max_number', 'remark',)
        widgets = {
            'date': DateTimePickerInput(
                options={
                    "locale": "ko",
                }
            ),
        }


# UnitFormset = modelformset_factory(CreateUnitForm, fields=('place', 'date', 'period', 'max_number', 'remark', ), extra=1)


RecordScoreFormSet = modelformset_factory(Record, fields=('score', ), extra=0)

class ModifyStudentForm(forms.ModelForm):
    class Meta():
        model = Student
        fields = ('student_number', 'major',)

class ModifyProfForm(forms.ModelForm):
    class Meta():
        model = Prof
        fields = ('prof_number', 'major',)
