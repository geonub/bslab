from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, Student, Prof, Research, Record

class StudentInline(admin.StackedInline):
    model = Student

class ProfInline(admin.StackedInline):
    model = Prof

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (StudentInline, ProfInline)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'sex',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student', 'is_prof')}))

    list_display = ('email', 'name', 'sex', 'is_active', 'is_superuser', 'is_student', 'is_prof', 'date_joined') #무엇을 노출
    search_fields = ('email', 'name', 'sex', 'is_active', 'is_superuser', 'is_student', 'is_prof', 'date_joined')
    ordering = ('email', 'name', 'sex', 'is_active', 'is_student', 'is_prof', 'date_joined')

class StudentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Personal info', {'fields': ('student_number', 'user', 'major',)}),
    )
    list_display = ('student_number', 'user', 'major', )
    search_fields = ('student_number', 'user', 'major', )
    ordering = ('student_number', 'user', 'major', )

class ProfAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Personal info', {'fields': ('prof_number', 'user', 'major',) }),
    )
    list_display = ('prof_number',  'user', 'major', )
    search_fields = ('prof_number', 'user', 'major', )
    ordering = ('prof_number', 'user', 'major', )

class ResearchAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Research info', {'fields': ('research_number', 'title', 'prof', 'year', 'semester', 'description', 'current_number', 'max_number', 'start_time', 'hour', 'minute',)}),
    )
    list_display = ('research_number', 'title', 'prof', 'year', 'semester', 'current_number', 'max_number', 'created_date', 'start_time', 'hour', 'minute',)
    search_fields = ('research_number', 'title', 'prof', 'year', 'semester', 'current_number', 'max_number', 'created_date', 'start_time', 'hour', 'minute',)
    ordering = ('research_number', 'title', 'prof', 'year', 'semester', 'current_number', 'max_number', 'created_date', 'start_time', 'hour', 'minute',)

class RecordAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Record info', {'fields': ('score', )}),
    )
    list_display = ('score', )
    search_fields = ('score', )
    ordering = ('title', 'student',)

# Register your models here.
admin.site.register(Student, StudentAdmin)
admin.site.register(Prof, ProfAdmin)
admin.site.register(Research, ResearchAdmin)
admin.site.register(Record, RecordAdmin)
