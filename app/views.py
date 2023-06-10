import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg
from django.shortcuts import render, redirect
from pandas.errors import MergeError
from app.models import *
import app.admin
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

# #shubham k [27-04-2023] otp varification for both labors and farmers mobile number
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
# @api_view(['POST'])
# def hello_world(request):
#     data = request.data
#
#     if data.get('phone_number') is None:
#         return Response({
#             'status': 400,
#             'message': 'key phone_number is required'
#         })
#
#     if data.get('Password') is None:
#         return Response({
#             'status': 400,
#             'message': 'key Password is required'
#         })
#
# #end of otp varification method



class Preprocessor(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        doc = re.sub("[^a-zA-Z]", " ", doc)
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]


def index(request):
    try:
        return render(request, 'app/index.html')
    except Exception as ex:
        return render(request, 'app/index.html', {'message': ex})


def login(request):
    try:
        if request.method == 'POST':
            mobile = str(request.POST.get("mobile")).strip()
            password = str(request.POST.get("password")).strip()
            role = str(request.POST.get("role")).strip()
            if role == 'admin':
                if mobile == app.admin.mobile and password == app.admin.password:
                    request.session['alogin'] = True
                    return redirect(viewfarmers)
            elif role == 'farmer':
                farmer = Farmer.objects.get(mobile=mobile)
                if farmer.password == password:
                    request.session['flogin'] = True
                    request.session['fmobile'] = mobile
                    request.session['fname'] = farmer.name
                    return redirect(uploadtask)
            else:
                labour = Labour.objects.get(mobile=mobile)
                if labour.password == password:
                    request.session['llogin'] = True
                    request.session['lmobile'] = mobile
                    request.session['lname'] = labour.name
                    request.session['lskills'] = labour.skills
                    return redirect(alltask)
            message = 'Invalid username or password'
            return render(request, 'app/login.html', {'message': message})
        else:
            request.session['alogin'] = False
            request.session['flogin'] = False
            return render(request, 'app/login.html')
    except Farmer.DoesNotExist:
        message = 'Invalid username or password'
    except Labour.DoesNotExist:
        message = 'Invalid username or password'
    except Exception as ex:
        message = ex
    return render(request, 'app/login.html', {'message': message})


def viewfarmers(request):
    if 'alogin' in request.session and request.session['alogin']:
        ds = Farmer.objects.all()
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            farmers = paginator.page(page_number)
        except PageNotAnInteger:
            farmers = paginator.page(1)
        except EmptyPage:
            farmers = paginator.page(paginator.num_pages)
        return render(request, 'admin/viewfarmers.html', {'farmers': farmers})
    else:
        return redirect(login)


def viewlabours(request):
    if 'alogin' in request.session and request.session['alogin']:
        ds = Labour.objects.all()
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            labours = paginator.page(page_number)
        except PageNotAnInteger:
            labours = paginator.page(1)
        except EmptyPage:
            labours = paginator.page(paginator.num_pages)
        return render(request, 'admin/viewlabours.html', {'labours': labours})
    else:
        return redirect(login)


def fregistration(request):
    if request.method == 'POST':
        try:
            farmer = Farmer()
            farmer.mobile = str(request.POST.get('mobile')).strip()
            farmer.name = request.POST.get('name')
            farmer.address = request.POST.get('address')
            farmer.password = str(request.POST.get('password')).strip()
            farmer.save(force_insert=True)
            message = 'Farmer registration done'
        except Exception as ex:
            message = ex
        return render(request, 'app/fregistration.html', {'message': message})
    else:
        return render(request, 'app/fregistration.html')


def uploadtask(request):
    try:
        if 'flogin' in request.session and request.session['flogin']:
            message = ''
            if request.method == 'POST':
                if request.FILES:
                    id = datetime.datetime.now().strftime('%d%m%y%I%M%S')
                    workimage = request.FILES['workimage1']
                    with open(f'media/task/{id}1.jpg', 'wb') as fw:
                        fw.write(workimage.read())
                    workimage = request.FILES['workimage2']
                    with open(f'media/task/{id}2.jpg', 'wb') as fw:
                        fw.write(workimage.read())
                    task = Task()
                    task.id = id
                    task.mobile = request.session['fmobile']
                    task.farmer = request.session['fname']
                    task.work = str(request.POST.get('work')).strip()
                    task.status = 'pending'
                    task.save(force_insert=True)
                    message = 'Task uploaded successfully'
        else:
            return redirect(login)
    except Exception as ex:
        message = ex
    return render(request, 'farmer/uploadtask.html', {'message': message})


def viewtask(request):
    if 'flogin' in request.session and request.session['flogin']:
        if request.method == 'POST':
            id = str(request.POST.get('id')).strip()
            task = Task.objects.get(id=id)
            task.delete()
        mobile = request.session['fmobile']
        ds = Task.objects.filter(mobile=mobile)
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            tasks = paginator.page(page_number)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        return render(request, 'farmer/viewtask.html', {'tasks': tasks})
    else:
        return redirect(login)


def changepassfarmer(request):
    if 'flogin' in request.session and request.session['flogin']:
        try:
            message = ''
            if request.method == 'POST':
                mobile = request.session['fmobile']
                farmer = Farmer.objects.get(mobile=mobile)
                oldpassword = str(request.POST.get('oldpassword')).strip()
                newpassword = str(request.POST.get('newpassword')).strip()
                if farmer.password == oldpassword:
                    farmer.password = newpassword
                    farmer.save(force_update=True)
                    message = 'Password changed successfully'
                else:
                    raise Exception('Password not match')
        except Exception as ex:
            message = ex
        return render(request, 'farmer/changepassword.html', {'message': message})
    else:
        return redirect(login)


def lregistration(request):
    if request.method == 'POST':
        try:
            message = ''
            if request.FILES:
                mobile = str(request.POST.get('mobile')).strip()
                idproof = request.FILES['idproof']
                with open(f'media/labour/{mobile}.jpg', 'wb') as fw:
                    fw.write(idproof.read())
                labour = Labour()
                labour.mobile = mobile
                labour.name = request.POST.get('name')
                labour.address = request.POST.get('address')
                labour.skills = request.POST.get('skills')
                labour.password = str(request.POST.get('password')).strip()
                labour.save(force_insert=True)
                message = 'Labour registration done'
        except Exception as ex:
            message = ex
        return render(request, 'app/lregistration.html', {'message': message})
    else:
        return render(request, 'app/lregistration.html')


def alltask(request):
    if 'llogin' in request.session and request.session['llogin']:
        lmobile = request.session['lmobile']
        lskills = request.session['lskills']
        if request.method == 'POST':
            id = datetime.datetime.now().strftime('%d%m%y%I%M%S')
            taskid = str(request.POST.get('id')).strip()
            task = Task.objects.get(id=taskid)
            if 'accept' in request.POST:
                lstatus = 'accepted'
                fstatus = 'pending'
            else:
                lstatus = 'rejected'
                fstatus = 'NA'
            workstatus = WorkStatus()
            workstatus.id = id
            workstatus.taskid = taskid
            workstatus.fname = task.farmer
            workstatus.fmobile = task.mobile
            workstatus.task = task.work
            workstatus.lmobile = lmobile
            workstatus.lname = request.session['lname']
            workstatus.lstatus = lstatus
            workstatus.fstatus = fstatus
            workstatus.lskills = lskills
            workstatus.save(force_insert=True)
        workstatus = WorkStatus.objects.filter(lmobile=lmobile)
        if workstatus:
            ids = [x.taskid for x in workstatus]
            ds = pd.DataFrame(list(Task.objects.filter(status='pending').exclude(id__in=ids).values()))
        else:
            ds = pd.DataFrame(list(Task.objects.filter(status='pending').values()))
        ds = ds.to_dict(orient='records')
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            tasks = paginator.page(page_number)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        return render(request, 'labour/alltask.html', {'tasks': tasks})
    else:
        return redirect(login)


def recommendation(request):
    if 'llogin' in request.session and request.session['llogin']:
        lmobile = request.session['lmobile']
        lskills = request.session['lskills']
        if request.method == 'POST':
            id = datetime.datetime.now().strftime('%d%m%y%I%M%S')
            taskid = str(request.POST.get('id')).strip()
            task = Task.objects.get(id=taskid)
            if 'accept' in request.POST:
                lstatus = 'accepted'
                fstatus = 'pending'
            else:
                lstatus = 'rejected'
                fstatus = 'NA'
            workstatus = WorkStatus()
            workstatus.id = id
            workstatus.taskid = taskid
            workstatus.fname = task.farmer
            workstatus.fmobile = task.mobile
            workstatus.task = task.work
            workstatus.lmobile = lmobile
            workstatus.lname = request.session['lname']
            workstatus.lstatus = lstatus
            workstatus.fstatus = fstatus
            workstatus.lskills = lskills
            workstatus.save(force_insert=True)
        workstatus = WorkStatus.objects.filter(lmobile=lmobile)
        if workstatus:
            ids = [x.taskid for x in workstatus]
            ds = pd.DataFrame(list(Task.objects.filter(status='pending').exclude(id__in=ids).values()))
        else:
            ds = pd.DataFrame(list(Task.objects.filter(status='pending').values()))
        if ds.shape[0] > 2:
            vectorizer = TfidfVectorizer(tokenizer=Preprocessor(),
                                         strip_accents='unicode',
                                         stop_words='english',
                                         lowercase=True)
            tasks = vectorizer.fit_transform(ds['work'])
            true_k = int(ds.shape[0] / 2) + 1
            model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
            labels = model.fit_predict(tasks)
            ds['labels'] = labels
            skills = vectorizer.transform([lskills])
            label = model.predict(skills)[0]
            ds = ds[ds['labels'] == label]
            ds = ds.to_dict(orient='records')
        else:
            ds = pd.DataFrame()
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            tasks = paginator.page(page_number)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        return render(request, 'labour/recommendation.html', {'tasks': tasks})
    else:
        return redirect(login)


def work(request):
    if 'llogin' in request.session and request.session['llogin']:
        lmobile = request.session['lmobile']
        ds = WorkStatus.objects.filter(lmobile=lmobile, lstatus='accepted', fstatus='accepted')
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            tasks = paginator.page(page_number)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        return render(request, 'labour/work.html', {'tasks': tasks})
    else:
        return redirect(login)


def workrequest(request):
    if 'flogin' in request.session and request.session['flogin']:
        fmobile = request.session['fmobile']
        if request.method == 'POST':
            id = str(request.POST.get('id')).strip()
            workstatus = WorkStatus.objects.get(id=id)
            task = Task.objects.get(id=workstatus.taskid)
            if 'accept' in request.POST:
                fstatus = 'accepted'
                workstatus.fstatus = fstatus
                workstatus.save(force_update=True)
                task.status = fstatus
                task.save(force_update=True)
                try:
                    ratings = Ratings()
                    ratings.lmobile = workstatus.lmobile
                    ratings.fmobile = workstatus.fmobile
                    ratings.fname = workstatus.fname
                    ratings.lname = workstatus.lname
                    ratings.ratings = 0
                    ratings.save(force_insert=True)
                except:
                    pass
                workstatus = WorkStatus.objects.filter(taskid=task.id, fstatus='pending')
                for ob in workstatus:
                    ob.fstatus = 'rejected'
                    ob.save(force_update=True)
            else:
                fstatus = 'rejected'
                workstatus.fstatus = fstatus
                workstatus.save(force_update=True)
        try:
            ratings = pd.DataFrame(list(Ratings.objects.values('lmobile').order_by('lmobile').annotate(
                total_ratings=Avg('ratings'))))
            ds = pd.DataFrame(
                list(WorkStatus.objects.filter(fmobile=fmobile, lstatus='accepted', fstatus='pending').values()))
            ds = pd.merge(ds, ratings)
            ds = ds.to_dict(orient='records')
            if not ds:
                raise MergeError
        except MergeError:
            ds = WorkStatus.objects.filter(fmobile=fmobile, lstatus='accepted', fstatus='pending')
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            tasks = paginator.page(page_number)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        return render(request, 'farmer/workrequest.html', {'tasks': tasks})
    else:
        return redirect(login)


def workassigned(request):
    if 'flogin' in request.session and request.session['flogin']:
        fmobile = request.session['fmobile']
        ds = WorkStatus.objects.filter(fmobile=fmobile, lstatus='accepted', fstatus='accepted')
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            tasks = paginator.page(page_number)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        return render(request, 'farmer/workassigned.html', {'tasks': tasks})
    else:
        return redirect(login)


def ratings_(request):
    if 'flogin' in request.session and request.session['flogin']:
        fmobile = request.session['fmobile']
        if request.method == 'POST':
            lmobile = str(request.POST.get('lmobile')).strip()
            fmobile = str(request.POST.get('fmobile')).strip()
            rating = str(request.POST.get('rating')).strip()
            ratings = Ratings.objects.get(lmobile=lmobile, fmobile=fmobile)
            ratings.ratings = rating
            ratings.save(force_update=True)
        ds = Ratings.objects.filter(fmobile=fmobile)
        page_number = request.GET.get('page')
        paginator = Paginator(ds, 5)
        try:
            ratings = paginator.page(page_number)
        except PageNotAnInteger:
            ratings = paginator.page(1)
        except EmptyPage:
            ratings = paginator.page(paginator.num_pages)
        return render(request, 'farmer/ratings.html', {'ratings': ratings})
    else:
        return redirect(login)


def changepasslabour(request):
    if 'llogin' in request.session and request.session['llogin']:
        try:
            message = ''
            if request.method == 'POST':
                mobile = request.session['lmobile']
                labour = Labour.objects.get(mobile=mobile)
                oldpassword = str(request.POST.get('oldpassword')).strip()
                newpassword = str(request.POST.get('newpassword')).strip()
                if labour.password == oldpassword:
                    labour.password = newpassword
                    labour.save(force_update=True)
                    message = 'Password changed successfully'
                else:
                    raise Exception('Password not match')
        except Exception as ex:
            message = ex
        return render(request, 'labour/changepassword.html', {'message': message})
    else:
        return redirect(login)
