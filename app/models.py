from django.db import models
from viewflow.fields import CompositeKey

#shubham k [27-04-2023] otp varification for both labors and farmers mobile number
# from django.contrib.auth.models import AbstractUser
# from .manager import UserManager
# class User(AbstractUser):
#     phone_number = models.CharField(max_length=12, unique=True)
#     is_phone_varified = models.BooleanField(default=False)
#     otp = models.CharField(max_length=6)
#
#     USERNAME_FIELD = 'phone_number'
#     REQUIRED_FIELDS = []
#     objects = UserManager()

#end of otp varification method

class Farmer(models.Model):
    mobile = models.TextField(primary_key=True)
    name = models.TextField()
    address = models.TextField()
    password = models.TextField()

    class Meta:
        db_table = 'tblFarmer'


class Task(models.Model):
    id = models.TextField(primary_key=True)
    mobile = models.TextField()
    farmer = models.TextField()
    work = models.TextField()
    status = models.TextField()

    class Meta:
        db_table = 'tblTask'


class Labour(models.Model):
    mobile = models.TextField(primary_key=True)
    name = models.TextField()
    address = models.TextField()
    skills = models.TextField()
    password = models.TextField()

    class Meta:
        db_table = 'tblLabour'


class WorkStatus(models.Model):
    id = models.TextField(primary_key=True)
    taskid = models.TextField()
    fname = models.TextField()
    fmobile = models.TextField()
    task = models.TextField()
    lmobile = models.TextField()
    lname = models.TextField()
    lskills = models.TextField()
    lstatus = models.TextField()
    fstatus = models.TextField()

    class Meta:
        db_table = 'tblWorkStatus'


class Ratings(models.Model):
    id = CompositeKey(columns=['lmobile', 'fmobile'])
    lmobile = models.TextField()
    fmobile = models.TextField()
    fname = models.TextField()
    lname = models.TextField()
    ratings = models.BigIntegerField()

    class Meta:
        db_table = 'tblRatings'
        unique_together = (('lmobile', 'fmobile'),)
