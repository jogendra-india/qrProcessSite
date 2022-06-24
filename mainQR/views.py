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
import mimetypes
from collections import defaultdict
import time
from threading import Thread
from datetime import datetime



def download_file(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'oracle_files.zip'
    # Define the full file path
    filepath = BASE_DIR + '/static/mainQR/' + filename
    # Open the file for reading content
    # path = open(filepath, 'r')
    # Set the mime type
    # mime_type, _ = mimetypes.guess_type(filepath)
    # # Set the return value of the HttpResponse
    # response = HttpResponse(path, content_type=mime_type)
    # # Set the HTTP header for sending to browser
    # response['Content-Disposition'] = "attachment; filename=%s" % filename
    # # Return the response value
    # return response


    zip_file = open(filepath, 'rb')
    response = HttpResponse(zip_file, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'oracle_files.zip'
    return response


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


def emp_liveStatus():


    while True:
        # try:
        mydb_db = mysql.connector.connect(
        # host="localhost", user="root", password="Bhel@123",
        host='10.9.100.109', user='bars', password='Bhel@123',
        database="tams")

        mycursor = mydb_db.cursor()


        sql_query = "Select id,ip,user,pass from livemonitoring"
        mycursor.execute(sql_query)
        my_result = mycursor.fetchall()

        for each_one in my_result:
            try:
                mydb_db_temp = mysql.connector.connect(
                # host="localhost", user="root", password="Bhel@123",
                host=each_one[1], user=each_one[2], password=each_one[3],
                database="tams")

                cursor = mydb_db_temp.cursor()

                cursor.execute("SELECT VERSION()")
                results = cursor.fetchone()
                ver = results[0]

                if (ver is None):

                    now1 = datetime.now()
                    dtString_dbb = now1.strftime('%Y-%m-%d %H:%M:%S')

                    mydb_db_temp_new = mysql.connector.connect(
                    # host="localhost", user="root", password="Bhel@123",
                    host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
            database="tams")

                    cursor_new = mydb_db_temp_new.cursor()

                    queries ="update livemonitoring set status='{}',last_checked='{}' where id={}".format('0',dtString_dbb,each_one[0])
                    cursor_new.execute(queries)
                    mydb_db_temp_new.commit()



                else:



                    now1 = datetime.now()
                    dtString_dbb = now1.strftime('%Y-%m-%d %H:%M:%S')

                    mydb_db_temp_new = mysql.connector.connect(
                    # host="localhost", user="root", password="Bhel@123",
                    host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
            database="tams")

                    cursor_new = mydb_db_temp_new.cursor()

                    queries ="update livemonitoring set status='{}',last_checked='{}' where id={}".format('1',dtString_dbb,each_one[0])

                    cursor_new.execute(queries)
                    mydb_db_temp_new.commit()


            except:

                now1 = datetime.now()
                dtString_dbb = now1.strftime('%Y-%m-%d %H:%M:%S')

                mydb_db_temp_new = mysql.connector.connect(
                # host="localhost", user="root", password="Bhel@123",
                host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
            database="tams")

                cursor_new = mydb_db_temp_new.cursor()

                queries ="update livemonitoring set status='{}',last_checked='{}' where id={}".format('0',dtString_dbb,each_one[0])
                cursor_new.execute(queries)
                mydb_db_temp_new.commit()

        time.sleep(900)



myThread = Thread(target=emp_liveStatus)
myThread.start()


@login_required(login_url='login')
def liveStatus(request,id1):
    
    # try:
    mydb_db = mysql.connector.connect(
        # host="localhost", user="root", password="Bhel@123",
        host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
        database="qrsite")

    mycursor = mydb_db.cursor()

    
    sql_query = "Select id,name, dob, unit,admin from emp_details where staff_no='{}'".format(id1)

    mycursor.execute(sql_query)
    
    my_result = mycursor.fetchall()

    for i in my_result:
        row_id,name, dob, unit,admin=i[0],i[1],i[2],i[3],i[4]

    


    mydb_db = mysql.connector.connect(
        # host="localhost", user="root", password="Bhel@123",
        host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'],
        database="tams")

    mycursor = mydb_db.cursor()

    dict_to_show={}


    if int(admin) == 0:

        sql_query = "Select ip,location,auth,status,last_checked from livemonitoring"
        mycursor.execute(sql_query)
        my_result = mycursor.fetchall()
        
        for each_entry in my_result:
            if each_entry[2] is not None:

                if ',' in each_entry[2]:
                    splitted=each_entry[2].split(',')
                    if id1 in splitted:
                        dict_to_show[each_entry[0]]=[each_entry[1],each_entry[3],each_entry[4]]
                elif each_entry[2]== id1:
                    dict_to_show[each_entry[0]]=[each_entry[1],each_entry[3],each_entry[4]]

    else:
        sql_query = "Select ip,location,auth,status,last_checked from livemonitoring"

        mycursor.execute(sql_query)
        
        my_result = mycursor.fetchall()
        for each_entry in my_result:
            dict_to_show[each_entry[0]]=[each_entry[1],each_entry[3],each_entry[4]]

    if id1 != str(request.user):
        return redirect("/logout")

    # print(context)
    # dict_to_show.update(context)
    context={"name":name,'admin':admin,'unit':unit,'staff_no':id1,'livedetails':dict_to_show}
    return render(request,"mainQR/livepage.html",context)


