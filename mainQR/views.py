from django.shortcuts import render,redirect
from urllib import request
from django.template import loader
from django.core.files.storage import FileSystemStorage
from random import randint
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import mysql.connector
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.contrib.auth.models import User



@csrf_exempt
def loginPage(request):

    

    check_logged_in = str(request.user)
    if check_logged_in != "AnonymousUser":
        return HttpResponseRedirect("/home/{}".format(check_logged_in))

    # print('this is',request.POST)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:

            login(request, user)
            if str(user)== 'adminhr':
                return HttpResponseRedirect("/team/{}".format(user))
            else:
                return HttpResponseRedirect("/home/{}".format(user))

        else:
            messages.error(request, 'Staff No. or Password is incorrect!!')
            return HttpResponseRedirect("/{}".format("login"))

    form = UserCreationForm()

    context = {'form': form}
    return render(request, 'mainQR/login.html', context)



@login_required(login_url='login')

def logoutUser(request):
    logout(request)


    messages.info(request, 'Logged Out Successfully!!')
    # return redirect("/{}".format(employee_staff_no))
    return redirect("/login")


@login_required(login_url='login')
def index(request,id):

    if id != str(request.user):
        return redirect("/logout")

    # try:
    mydb_db = mysql.connector.connect(
        # host="localhost", user="root", password="Bhel@123",
        host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
        database="qrsite")

    mycursor = mydb_db.cursor()

    
    sql_query = "Select id,name, dob, unit,admin from emp_details where staff_no='{}'".format(id)

    mycursor.execute(sql_query)
    
    my_result = mycursor.fetchall()

    for i in my_result:
        row_id,name, dob, unit,admin=i[0],i[1],i[2],i[3],i[4]
        


    # except:

    #     pass

    context={"name":name,'admin':admin,'unit':unit,'staff_no':id}

    
    return render(request,"mainQR/index.html",context)



@login_required(login_url='login')
def homepage(request,id):

    if id != str(request.user):
        return redirect("/logout")

    # try:
    mydb_db = mysql.connector.connect(
        # host="localhost", user="root", password="Bhel@123",
        host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
        database="qrsite")

    mycursor = mydb_db.cursor()

    
    sql_query = "Select id,name, dob, unit,admin from emp_details where staff_no='{}'".format(id)

    mycursor.execute(sql_query)
    
    my_result = mycursor.fetchall()

    for i in my_result:
        row_id,name, dob, unit,admin=i[0],i[1],i[2],i[3],i[4]
        
    # except:

    #     pass

    context={"name":name,'admin':admin,'unit':unit,'staff_no':id}

    
    return render(request,"mainQR/homepage.html",context)