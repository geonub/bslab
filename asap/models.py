from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.dates import MONTHS


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True,
                              help_text="""반드시 자신의 학교 이메일을 기입해야만 합니다.""")
    name = models.CharField(max_length=10)
    SEX = (
        ('M', '남자'),
        ('F', '여자'),
        )
    sex = models.CharField(max_length=1, choices=SEX)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_student = models.BooleanField('student status', default=False)
    is_prof = models.BooleanField('teacher status', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'sex']

    objects = UserManager()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_number = models.CharField(max_length=10)
    major = models.CharField(max_length=10)

    def __str__(self):
        return self.student_number

class Prof(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    prof_number = models.CharField(max_length=10)
    major = models.CharField(max_length=10)

    def __str__(self):
        return self.user.name

class Research(models.Model):
    research_number = models.CharField(max_length=6)
    prof = models.ForeignKey('Prof', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    SEME = (
        ('1', 'Spring'),
        ('2', 'Fall')
        )                                                                                                                                                                                                                                                                                                                                                                                            
    semester = models.CharField(max_length=1, choices=SEME)
    year = models.PositiveIntegerField(default=2018)
    month = models.PositiveSmallIntegerField(choices = MONTHS.items(), null=True)
    # 캘린더 기능 추가
    place = models.CharField(max_length=30, null=True)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    max_number = models.PositiveIntegerField(default=0)
    current_number = models.PositiveIntegerField(default=0)
    TIME_CHOICES = ( ('09:00:00', '09 AM'),
                    ('10:00:00', '10 AM'),
                    ('11:00:00', '11 AM'),
                    ('12:00:00', '12 PM'),
                    ('13:00:00', '01 PM'),
                    ('14:00:00', '02 PM'),
                    ('15:00:00', '03 PM'),
                    ('16:00:00', '04 PM'),
                    ('17:00:00', '05 PM'),
                    ('18:00:00', '06 PM'),
                    ('19:00:00', '07 PM'),
                    ('20:00:00', '08 PM'),
                    ('21:00:00', '09 PM'),
                    ('22:00:00', '10 PM'),
                    ('23:00:00', '11 PM'),
                    )
    start_time = models.CharField(max_length=8, choices = TIME_CHOICES, null=True)
    HOUR = ( ('00:00:00', '0시간'),
            ('01:00:00', '1시간'),
            ('02:00:00', '2시간'),
            ('03:00:00', '3시간'),
            ('04:00:00', '4시간'),
            ('05:00:00', '5시간'),
            )
    MINUTE = ( ('00:00:00', '0분'),
            ('00:15:00', '15분'),
            ('00:30:00', '30분'),
            ('00:45:00', '45분'),
            )
    hour = models.CharField(max_length=8, choices = HOUR, null=True)
    minute = models.CharField(max_length=8, choices = MINUTE, null=True)

    def __str__(self):
        return self.title

class Record(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    title = models.ForeignKey('Research', on_delete=models.CASCADE)
    total = models.PositiveIntegerField(null=True, blank=True)
    SCORE = (
        ('P', 'P'),
        ('F', 'F'),
    )
    score = models.CharField(max_length=2, choices=SCORE, null=True, blank=True)

    def __str__(self):
        return self.title.title + ' / ' + self.student.user.name

