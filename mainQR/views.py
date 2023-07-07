import json
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import mysql.connector
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import time
from threading import Thread
from datetime import datetime
from django.http import HttpResponse, Http404
from .models import EmpDetails


def download_file(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'oracle_files.zip'
    # Define the full file path
    filepath = BASE_DIR + '/static/mainQR/' + filename
    zip_file = open(filepath, 'rb')
    response = HttpResponse(zip_file, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'oracle_files.zip'
    return response

def download_exe(request, id):
    try:
        emp_details = EmpDetails.objects.get(staff_no=id)
        exe_access_to = emp_details.exe_access_to
        filename = None
        if exe_access_to == 'SSBG':
            filename = 'SSBG/BHELQEEE_SSBG.zip'
        elif exe_access_to == 'ROD':
            filename = 'ROD/BHELQEEE_ROD_2.zip'
        elif exe_access_to == 'CORP DELHI':
            filename = 'CORP/CORP_DELHI.zip'
        elif exe_access_to == 'RD':
            filename = 'RD/QFASE.zip'

        if filename:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = BASE_DIR + '/static/mainQR/exe_files/' + filename
            if os.path.exists(filepath):
                with open(filepath, 'rb') as zip_file:
                    response = HttpResponse(zip_file, content_type='application/force-download')
                    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
                    return response
            else:
                raise Http404("File not found")
        else:
            raise Http404("Filename not found")

    except EmpDetails.DoesNotExist:
        raise Http404("Employee details not found")

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

import mysql.connector
from django.http import HttpResponse

def setup_database(request):
    if request.method == 'POST':
        success_messages = []
        failure_messages = []
        ip_address_unit = request.POST.get('ipAddress')  # Retrieve the IP address from the form
        ip_address = ip_address_unit.split(',')[0].replace(' ', '')
        unit = ip_address_unit.split(',')[1]

        # SSBG and ROD (BHELQEEE is running) so
        # 1. create database tams if not exists
        database_creation_success = 0
        try:
            mydb_db_temp = mysql.connector.connect(
                host=ip_address, user='tams', password='Bhel@123'
            )
            mycursor = mydb_db_temp.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS tams")
            success_messages.append(f"Database 'tams' created on {ip_address}")

            # 2. Create bhelqeee_attendance table if not exists
            if 'SSBG' in unit or 'ROD' in unit:
                mycursor.execute("""
                    CREATE TABLE IF NOT EXISTS tams.`bhelqeee_attendance` (
                        `id` int NOT NULL AUTO_INCREMENT,
                        `staff_no` varchar(8) DEFAULT NULL,
                        `swipe` datetime DEFAULT NULL,
                        `mac` varchar(25) DEFAULT NULL,
                        `status` varchar(2) DEFAULT NULL,
                        PRIMARY KEY (`id`)
                    )
                """)
                success_messages.append(f"Table 'bhelqeee_attendance' created on {ip_address}")

                # 3. Create emp_details table if not exists
                mycursor.execute("""
                    CREATE TABLE IF NOT EXISTS tams.`emp_details` (
                        `id` int NOT NULL AUTO_INCREMENT,
                        `EMP_ID` varchar(10) DEFAULT NULL,
                        `EMP_NAME` varchar(100) DEFAULT NULL,
                        `EMP_BHEL_JN_DATE` varchar(10) DEFAULT NULL,
                        PRIMARY KEY (`id`),
                        UNIQUE KEY `EMP_ID` (`EMP_ID`)
                    )
                """)
                success_messages.append(f"Table 'emp_details' created on {ip_address}")
                database_creation_success = 1
            elif 'RD' in unit:
                mycursor.execute("CREATE DATABASE IF NOT EXISTS attendance_data")
                success_messages.append(f"Database 'attendance_data' created on {ip_address}")
                mycursor.execute("""
                        CREATE TABLE IF NOT EXISTS attendance_data.`attendance_new` (
                        `id` int NOT NULL AUTO_INCREMENT,
                        `staff_no` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        `date` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        `time` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        `swipe` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        `type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        PRIMARY KEY (`id`)
                        )
                """)
                success_messages.append(f"Table 'attendance_data' created on {ip_address}")
                mycursor.execute("""
                                CREATE TABLE IF NOT EXISTS attendance_data.`face_testing` (
                                `id` int NOT NULL AUTO_INCREMENT,
                                `staff_no` varchar(10) DEFAULT NULL,
                                `predicted_staff_no` varchar(10) DEFAULT NULL,
                                `confidence` varchar(50) DEFAULT NULL,
                                `eudistance` varchar(50) DEFAULT NULL,
                                `face_extraction_type` varchar(2) DEFAULT NULL,
                                `face_model_type` varchar(2) DEFAULT NULL,
                                `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                PRIMARY KEY (`id`)
                                )
                """)
                success_messages.append(f"Table 'face_testing' created on {ip_address}")
                # 3. Create emp_details table if not exists
                mycursor.execute("""
                                CREATE TABLE IF NOT EXISTS attendance_data.`pass` (
                                `id` int NOT NULL AUTO_INCREMENT,
                                `date` varchar(10) DEFAULT NULL,
                                `req_by_staff` varchar(10) DEFAULT NULL,
                                `req_type` varchar(10) DEFAULT NULL,
                                `time_out` varchar(20) DEFAULT NULL,
                                `fetched_id` int DEFAULT NULL,
                                `current_status` varchar(10) DEFAULT NULL,
                                PRIMARY KEY (`id`),
                                UNIQUE KEY `fetched_id` (`fetched_id`)
                                )
                """)
                success_messages.append(f"Table 'pass' created on {ip_address}")
                database_creation_success = 1

            elif 'CORP ' in unit:
                mycursor.execute("""
                        CREATE TABLE IF NOT EXISTS tams.`bhelqeee_attendance` (
                        `id` int NOT NULL AUTO_INCREMENT,
                        `staff_no` varchar(8) DEFAULT NULL,
                        `swipe` datetime DEFAULT NULL,
                        `mac` varchar(25) DEFAULT NULL,
                        `status` varchar(2) DEFAULT NULL,
                        PRIMARY KEY (`id`)
                        )
                """)
                success_messages.append(f"Table 'bhelqeee_attendance' created on {ip_address}")
                mycursor.execute("""
                            CREATE TABLE IF NOT EXISTS tams.`bhelqeee_face_attendance` (
                            `id` int NOT NULL AUTO_INCREMENT,
                            `staff_no` varchar(8) DEFAULT NULL,
                            `swipe` datetime DEFAULT NULL,
                            `mac` varchar(25) DEFAULT NULL,
                            `status` varchar(2) DEFAULT NULL,
                            PRIMARY KEY (`id`)
                            )
                """)
                success_messages.append(f"Table 'bhelqeee_face_attendance' created on {ip_address}")
                # 3. Create emp_details table if not exists
                mycursor.execute("""
                        CREATE TABLE IF NOT EXISTS tams.`face_testing` (
                        `id` int NOT NULL AUTO_INCREMENT,
                        `staff_no` varchar(10) DEFAULT NULL,
                        `predicted_staff_no` varchar(10) DEFAULT NULL,
                        `confidence` varchar(50) DEFAULT NULL,
                        `eudistance` varchar(50) DEFAULT NULL,
                        `face_extraction_type` varchar(2) DEFAULT NULL,
                        `face_model_type` varchar(2) DEFAULT NULL,
                        `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        PRIMARY KEY (`id`)
                        )
                """)
                success_messages.append(f"Table 'face_testing' created on {ip_address}")

                mycursor.execute("""
                        CREATE TABLE IF NOT EXISTS tams.`testing_parameters` (
                        `face_extraction` varchar(2) DEFAULT NULL,
                        `face_model` varchar(2) DEFAULT NULL
                        )
                """)
                success_messages.append(f"Table 'testing_parameters' created on {ip_address}")
                database_creation_success = 1
        
        except mysql.connector.Error as e:
            failure_messages.append(str(e))
        
        # Now add live monitoring and syncing
        try:
            if 'RD' not in unit and database_creation_success == 1:
                mydb_db_temp = mysql.connector.connect(
                    host='10.9.100.109', user='tams', password='Bhel@123'
                )
                if 'SSBG' in unit or 'ROD' in unit:
                    query = f"INSERT INTO tams.`ipAddress` (`ip`, `user`, `pass`, `location`) \
                            SELECT '{ip_address}', 'tams', 'Bhel@123', '{unit}' \
                            WHERE NOT EXISTS (SELECT 1 FROM tams.`ipAddress` WHERE `ip` = '{ip_address}')"

                    mycursor = mydb_db_temp.cursor()
                    mycursor.execute(query)
                    mydb_db_temp.commit()

                    if mycursor.rowcount > 0:
                        success_messages.append(f'Record inserted in ipAddress table for IP: {ip_address}')
                    else:
                        success_messages.append(f'IP: {ip_address} already exists in ipAddress table')

                elif 'CORP' in unit:
                    query = f"INSERT INTO tams.`ipAddressFace` (`ip`, `user`, `pass`, `location`) \
                            SELECT '{ip_address}', 'tams', 'Bhel@123', '{unit}' \
                            WHERE NOT EXISTS (SELECT 1 FROM tams.`ipAddressFace` WHERE `ip` = '{ip_address}')"

                    mycursor = mydb_db_temp.cursor()
                    mycursor.execute(query)
                    mydb_db_temp.commit()

                    if mycursor.rowcount > 0:
                        success_messages.append(f'Record inserted in ipAddressFace table for IP: {ip_address}')
                    else:
                        success_messages.append(f'IP: {ip_address} already exists in ipAddressFace table')
                    
        except Exception as e:
            failure_messages.append(f'Error occurred while inserting record in ipAddress table: {str(e)}')

        # Finally add for live monitoring
        try:
            if database_creation_success == 1:
                mydb_db_temp = mysql.connector.connect(
                    host='10.9.100.109', user='tams', password='Bhel@123'
                )
                query = f"INSERT INTO tams.`livemonitoring` (`ip`, `user`, `pass`, `location`, `auth`, `status`, `last_checked`, `last_online`) \
                            SELECT '{ip_address}', 'tams', 'Bhel@123', '{unit}', NULL, 1, NULL, NULL \
                            WHERE NOT EXISTS (SELECT 1 FROM tams.`livemonitoring` WHERE `ip` = '{ip_address}')"

                mycursor = mydb_db_temp.cursor()
                mycursor.execute(query)
                mydb_db_temp.commit()

                if mycursor.rowcount > 0:
                    success_messages.append(f'Record inserted in livemonitoring table for IP: {ip_address}')
                else:
                    success_messages.append(f'IP: {ip_address} already exists in livemonitoring table')
        except Exception as e:
            failure_messages.append(f'Error occurred while inserting record in livemonitoring table: {str(e)}')

        # Process success and failure messages
        if failure_messages:
            response_data = {
                'success': False,
                'message': 'Failed to set up the database',
                'failure_messages': failure_messages
            }
        else:
            response_data = {
                'success': True,
                'message': 'Database setup successful',
                'success_messages': success_messages
            }

        return HttpResponse(json.dumps(response_data), content_type='application/json')

    # Handle GET request or other cases
    return HttpResponse('Invalid request method')


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

                    queries ="update livemonitoring set status='{}',last_checked='{}',last_online='{}' where id={}".format('1',dtString_dbb,dtString_dbb,each_one[0])

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

        sql_query = "Select ip,location,auth,status,last_checked,last_online from livemonitoring"
        mycursor.execute(sql_query)
        my_result = mycursor.fetchall()
        
        for each_entry in my_result:
            if each_entry[2] is not None:

                if ',' in each_entry[2]:
                    splitted=each_entry[2].split(',')
                    if id1 in splitted:
                        dict_to_show[each_entry[0]]=[each_entry[1],each_entry[3],each_entry[4],each_entry[5]]
                elif each_entry[2]== id1:
                    dict_to_show[each_entry[0]]=[each_entry[1],each_entry[3],each_entry[4],each_entry[5]]

    else:
        sql_query = "Select ip,location,auth,status,last_checked,last_online from livemonitoring"

        mycursor.execute(sql_query)
        
        my_result = mycursor.fetchall()
        for each_entry in my_result:
            dict_to_show[each_entry[0]]=[each_entry[1],each_entry[3],each_entry[4],each_entry[5]]

    if id1 != str(request.user):
        return redirect("/logout")

    # print(context)
    # dict_to_show.update(context)
    context={"name":name,'admin':admin,'unit':unit,'staff_no':id1,'livedetails':dict_to_show}
    return render(request,"mainQR/livepage.html",context)


