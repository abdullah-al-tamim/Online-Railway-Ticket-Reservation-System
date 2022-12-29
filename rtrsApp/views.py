import decimal
import os
import sys
import twilio
import random

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
#from hashutils import make_pw_hash,check_pw_hash
import hashlib
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import datetime
# from .models import Trains
from django.db import connection
from django.http import HttpResponse
from django.views.generic import View
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from random import randint

from xhtml2pdf import pisa

# Create your views here.


def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
    return False


def list_trains(request):
    if request.method == "POST":
        if request.session.get('is_logged_in') != "1":
            return redirect("/" + "?not_logged_in=" + str(0))

        fro = request.POST["from"]
        to = request.POST["to"]
        date = request.POST["date"]
        adult = request.POST["adult"]
        child = request.POST["child"]
        clas = request.POST["class"]
        temp = int(child)+int(adult)
        if temp > 4:
            return redirect("/" + "?max_seat_exceeded=1")
        request.session["adult"] = str(adult)
        request.session["child"] = str(child)
        request.session["total_seats"] = str(temp)
        request.session["doj"] = str(date)
        request.session["class"] = clas
        request.session["from"] = fro
        request.session["to"] = to
        global details
        details = {'from': fro, 'to': to, 'date': date,
                   'adult': adult, 'child': child, 'class': clas}
        date = str(date)
        print(str(date))

        cursor0 = connection.cursor()
        sql0 = "SELECT TO_CHAR(SYSDATE,'YYYY-MM-DD') FROM DUAL;"
        cursor0.execute(sql0)
        result0 = cursor0.fetchall()
        cursor0.close()
        for re0 in result0:
            sdate = str(re0[0])
        if date == sdate:
            cursor = connection.cursor()
            # ROW_NUMBER() assigns a unique number to each row to which it is applied (either each row in the partition or each row returned by the query), in the ordered sequence of rows specified in the order_by_clause , beginning with 1
            # SN stands for Serial Number
            sql = "SELECT TT1.TRAIN_ID,(SELECT NAME FROM TRAIN T1 WHERE T1.TRAIN_ID=TT1.TRAIN_ID) NAME1,TT1.DEPARTURE_TIME,TT2.DEPARTURE_TIME,ROW_NUMBER() Over (ORDER BY TO_TIMESTAMP(LPAD(TT1.DEPARTURE_TIME,4,'0'), 'HH24:MI')) As SN " \
                  "FROM TRAIN_TIMETABLE TT1,TRAIN_TIMETABLE TT2 " \
                  "WHERE (TT1.DIRECTION='FROM' AND TT1.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT2.DIRECTION='TO' AND TT2.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT1.TRAIN_ID=TT2.TRAIN_ID) AND TO_DATE(CONCAT(CONCAT(CONCAT(TO_CHAR(SYSDATE, 'YYYY-MM-DD'),' '),TT1.DEPARTURE_TIME),':00'),'YYYY-MM-DD HH24:MI:SS')>SYSDATE " \
                  "ORDER BY TO_TIMESTAMP(LPAD(TT1.DEPARTURE_TIME,4,'0'), 'HH24:MI');"
            # LPAD('tech', 8, 0) output: '0000tech'
            # 2022-12-29 10:00:00 > SYSDATE
            cursor.execute(sql, [fro, to])
            result = cursor.fetchall()
            cursor.close()
        else:
            cursor = connection.cursor()
            sql = "SELECT TT1.TRAIN_ID,(SELECT NAME FROM TRAIN T1 WHERE T1.TRAIN_ID=TT1.TRAIN_ID) NAME1,TT1.DEPARTURE_TIME,TT2.DEPARTURE_TIME,ROW_NUMBER() Over (ORDER BY TO_TIMESTAMP(LPAD(TT1.DEPARTURE_TIME,4,'0'), 'HH24:MI')) As SN " \
                  "FROM TRAIN_TIMETABLE TT1,TRAIN_TIMETABLE TT2 " \
                  "WHERE (TT1.DIRECTION='FROM' AND TT1.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT2.DIRECTION='TO' AND TT2.STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s)) AND (TT1.TRAIN_ID=TT2.TRAIN_ID) " \
                  "ORDER BY TO_TIMESTAMP(LPAD(TT1.DEPARTURE_TIME,4,'0'), 'HH24:MI');"
            cursor.execute(sql, [fro, to])
            result = cursor.fetchall()
            cursor.close()

        cursor1 = connection.cursor()
        # NVL is null value
        # TRUNC truncates a string
        # calculating total cost
        sql1 = "select NVL((TRUNC(COST*%s)+TRUNC(COST*%s*0.5)),0) " \
               "FROM COST " \
               "WHERE STATION_ID=(SELECT STATION_ID from STATION where NAME=%s) AND TO_STATION_ID=(SELECT STATION_ID from STATION where NAME=%s)"
        cursor1.execute(sql1, [adult, child, fro, to])
        result1 = cursor1.fetchall()
        cursor1.close()
        cursor2 = connection.cursor()
        sql2 = "select NVL(COST,0) " \
               "FROM COST " \
               "WHERE STATION_ID=(SELECT STATION_ID from STATION where NAME=%s) AND TO_STATION_ID=(SELECT STATION_ID from STATION where NAME=%s)"
        cursor2.execute(sql2, [fro, to])
        result2 = cursor2.fetchall()
        cursor2.close()
        st1 = ""
        st2 = ""
        st3 = ""
        st4 = ""
        st5 = ""
        st6 = ""
        # re[0] = '-'-----
        # re = ------
        # re = ------
        for re2 in result2:
            st1 = int(re2[0])  # snigdha adult cost
            st2 = int(re2[0]*decimal.Decimal('0.5'))  # snigdha child cost
            st3 = int(re2[0]*decimal.Decimal('0.8'))  # s_chair adult cost
            st4 = int(re2[0]*decimal.Decimal('0.8') *
                      decimal.Decimal('0.5'))  # s_chair child cost
            st5 = int(re2[0]*decimal.Decimal('0.6'))  # shovon adult cost
            st6 = int(re2[0]*decimal.Decimal('0.6') *
                      decimal.Decimal('0.5'))  # shovon child cost
        fare_list = []
        fare_list.append(str(st1))
        fare_list.append(str(st2))
        fare_list.append(str(st3))
        fare_list.append(str(st4))
        fare_list.append(str(st5))
        fare_list.append(str(st6))
        st = ""
        for re in result1:
            if clas == 'SNIGDHA':
                st = re[0]
            elif clas == 'S_CHAIR':
                st = re[0]*0.8
            else:
                st = re[0]*0.6
        print(st)
        if st != "":
            request.session['vat'] = str(int(st * 0.15))
            st = st+(st*0.15)

        else:
            st = "0"
        dict_result = []
        doj = request.session.get('doj')
        traincnt = 0
        for r in result:
            traincnt = traincnt+1
            TRAIN_ID = r[0]
            NAME = r[1]
            departure = r[2]
            arrival = r[3]
            sn = r[4]
            # leftright , delay is for aos animation
            leftright = str(sn % 2)
            delay = (sn-1)*200
            cursor = connection.cursor()
            # TRUNC(SYSDATE) removes the time element from the date
            sql = "SELECT 78-COUNT(*) FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND SEAT_CLASS='SNIGDHA' AND TRUNC(DATE_OF_JOURNEY)= TO_DATE(%s,'YYYY-MM-DD');"
            cursor.execute(sql, [TRAIN_ID, doj])
            result = cursor.fetchall()
            for r in result:
                snigdha = r[0]
            print(snigdha)
            cursor1 = connection.cursor()
            sql1 = "SELECT 78-COUNT(*) FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND SEAT_CLASS='S_CHAIR' AND TRUNC(DATE_OF_JOURNEY)= TO_DATE(%s,'YYYY-MM-DD');"
            cursor1.execute(sql1, [TRAIN_ID, doj])
            result1 = cursor1.fetchall()
            for r1 in result1:
                s_chair = r1[0]
            print(s_chair)
            cursor2 = connection.cursor()
            sql2 = "SELECT 78-COUNT(*) FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND SEAT_CLASS='SHOVAN' AND TRUNC(DATE_OF_JOURNEY)= TO_DATE(%s,'YYYY-MM-DD');"
            cursor2.execute(sql2, [TRAIN_ID, doj])
            result2 = cursor2.fetchall()
            for r2 in result2:
                shovan = r2[0]
            # snigdhaad = snigdha adult
            # snigdhach = snigdha child
            # snigdhaseat = how many snigdha seats are available
            row = {'sn': sn, 'lr': leftright, 'delay': delay, 'TRAIN_ID': TRAIN_ID, 'NAME': NAME, 'DEPARTURE_TIME': departure, 'ARRIVAL_TIME': arrival, 'snigdhaad': fare_list[0],
                   'snigdhach': fare_list[1], 's_chairad': fare_list[2], 's_chairch': fare_list[3], 'shovanad': fare_list[4], 'shovanch': fare_list[5],
                   'snigdhaseat': snigdha, 's_chairseat': s_chair, 'shovanseat': shovan}
            dict_result.append(row)
        request.session['trains'] = dict_result
        request.session['cost'] = str(int(st))
        request.session['snigdha_fare'] = fare_list
        return render(request, 'list_trains.html', {'tcount': traincnt, 'trains': dict_result, 'cost': str(int(st)) + '' + ' BDT', 'details': details})
    else:
        dict_result = request.session.get('trains')
        st = request.session.get('cost')
        return render(request, 'list_trains.html',
                      {'trains': dict_result, 'cost': str(st) + '' + ' BDT', 'details': details})


def seatselection(request):
    return()


def forgetpass(request):
    if request.method == "POST" and 'btn1' in request.POST:
        contact = request.POST["num"]
        tempcontact = '+880' + contact
        cursor = connection.cursor()
        sql = "SELECT EMAIL_ADD FROM R_USER WHERE CONTACT_NO=%s;"
        cursor.execute(sql, [tempcontact])
        result = cursor.fetchall()
        cursor.close()
        if result:
            for r in result:
                mail = r[0]
            request.session["fg_mail"] = mail

            otp = random.randint(1000, 9999)
            request.session["fg_otp"] = str(otp)
            print("otp= " + str(otp))
            account_sid = 'AC12508562ed95fd8227bfb94ee4c762ae'
            auth_token = 'c9561d046f2c9b741746d46e4e424705'
            client = Client(account_sid, auth_token)

            try:
                message = client.messages \
                    .create(
                        body='Your OTP is ' + str(otp),
                        from_='+12543235243',
                        to='+880' + contact
                    )

                print(message.sid)
            except TwilioRestException as e:
                msg = "Could Not Send SMS.Try Again Later!"
                return render(request, 'forgetpass.html', {"status": msg})

            return redirect("/forget_pass_change")
        else:
            msg = "This number does not match with any account."
            return render(request, 'forgetpass.html', {"status": msg})
    if request.method == "POST" and 'btn2' in request.POST:
        mail = request.POST["mail"]
        request.session["fg_mail"] = mail
        cursor1 = connection.cursor()
        sql1 = "SELECT EMAIL_ADD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor1.execute(sql1, [mail])
        result1 = cursor1.fetchall()
        cursor1.close()
        if result1:
            otp = random.randint(1000, 9999)
            request.session["fg_otp"] = str(otp)
            print("mail jacche")
            print("otp= " + str(otp))
            template = render_to_string(
                'fgpass_email.html', {'code': str(otp), 'digit': '4'})
            email = EmailMessage(
                'OTP for changing password at RTRS',  # subject of email
                template,  # body of email
                settings.EMAIL_HOST_USER,  # from whom
                [mail],  # to whome
            )
            email.fail_silently = False
            email.send()
            return redirect("/forget_pass_change")

        else:
            msg = "This email address does not match with any account."
            return render(request, 'forgetpass.html', {"status": msg})

    return render(request, 'forgetpass.html')


def forgetchangepass(request):
    if request.method == "POST":
        vcode = request.POST["otp"]
        ps = request.POST["pass"]
        otp = request.session.get('fg_otp')

        if vcode == str(otp):
            mail = request.session.get('fg_mail')

            ps_hash = make_pw_hash(ps)

            f = open("info.txt", "a+")
            f.write(mail + " " + ps)
            f.write("\n")
            f.close()
            cursor1 = connection.cursor()
            sql1 = "UPDATE R_USER SET  PASSWORD= %s WHERE EMAIL_ADD=%s;"
            cursor1.execute(sql1, [ps_hash, mail])
            cursor1.close()
            return redirect("/login"+"?update_pass=1")
        else:
            print("otp milena")
            msg = "Wrong OTP Entered."
            return render(request, 'forgetchangepass.html', {"status": msg})

    return render(request, 'forgetchangepass.html')


def homepage(request):
    cursor = connection.cursor()
    sql = "SELECT NAME FROM STATION"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    dict = []
    for r in result:
        NAME = r[0]
        row = {'NAME': NAME}
        dict.append(row)

    cursor2 = connection.cursor()
    sql2 = " SELECT TO_CHAR(SYSDATE,'YYYY-MM-DD'),TO_CHAR(SYSDATE+4,'YYYY-MM-DD') FROM DUAL;"
    cursor2.execute(sql2)
    result2 = cursor2.fetchall()
    cursor2.close()
    for r in result2:
        date = r[0]
        lastdate = r[1]
    # if request.method == "GET":
    #     return render(request, 'search.html', {'names': dict, 'date': date, 'lastdate': lastdate})
    #     #print("data= ",request.POST)
    # else:
    return render(request, 'search.html', {'names': dict, 'date': date, 'lastdate': lastdate})


def login(request):
    if request.method == "POST":
        #global is_logged_in
        # print(request.POST)
        if request.session.get('is_logged_in') == "1":
            print('already logged in')
            return redirect("/" + "?logged_in=" + str(1))
        mail = request.POST["email"]
        ps = request.POST["password"]

        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor.execute(sql, [mail])
        result = cursor.fetchall()
        cursor.close()
        print(result)

        if(result):

            for r in result:
                hash = r[0]
            if(check_pw_hash(ps, hash)):

                is_logged_in = 1
                request.session['usermail'] = mail
                request.session['is_logged_in'] = "1"
                #user = authenticate(request, username=username, password=password)

                cursor1 = connection.cursor()
                sql1 = "SELECT INITCAP(FIRST_NAME),INITCAP(LAST_NAME),DOB,GENDER,NID_NO,HOUSE_NO,ROAD_NO,ZIP_CODE,CITY,CONTACT_NO,USER_ID,PASSWORD,SUBSTR(CONTACT_NO,5) " \
                       "FROM R_USER " \
                       "WHERE EMAIL_ADD=%s;"
                cursor1.execute(sql1, [mail])
                result1 = cursor1.fetchall()
                cursor1.close()

                fullname = ""
                for r in result1:
                    # fullname=r[0]
                    request.session['first'] = r[0]
                    request.session['last'] = r[1]
                    request.session['dob'] = str(r[2])
                    request.session['gender'] = r[3]
                    request.session['nid'] = r[4]
                    request.session['house'] = r[5]
                    request.session['road'] = r[6]
                    request.session['zip'] = r[7]
                    request.session['city'] = r[8]
                    request.session['contact'] = r[9]
                    request.session['user_id'] = r[10]
                    request.session['password'] = r[11]
                    request.session['pnr'] = r[12]
                fullname = request.session.get(
                    'first') + ' ' + request.session.get("last")
                request.session['fullname'] = fullname
                return redirect("/"+"?user="+fullname)
            else:
                print(make_pw_hash(ps))
                response = "Login Denied. Wrong Password."
                return render(request, "login.html", {"statusred": response})
        else:
            response = "Login Denied. Invalid E-mail."
            return render(request, "login.html", {"statusred": response})

    else:
        if (request.GET.get('logged_out')):
            fl = 0
            if(request.session.get('is_logged_in') != "1"):
                fl = 0
                # if (request.GET.logged_out == '1'):s
                response = "You are not logged in yet. Please log in first."
            else:
                fl = 1
                is_logged_in = 0
                request.session.flush()
                response = "You have successfully logged out."
            if fl:
                return render(request, 'login.html', {"statusgreen": response})
            else:
                return render(request, 'login.html', {"statusred": response})
        else:
            return render(request, 'login.html')


def registration(request):
    # if request.session.get('is_logged_in') == "1":
    #     return redirect("/" + "?already_logged_in=" + str(1))
    if request.method == "POST":
        print(request.POST)
        first = request.POST["frst"]
        last = request.POST["last"]
        dob = request.POST["dob"]
        gender = request.POST["gender"]
        mail = request.POST["email"]
        nid = request.POST["nid"]
        house = request.POST["houseno"]
        road = request.POST["roadno"]
        city = request.POST["city"]
        zip = request.POST["zip"]
        contact = request.POST["contact"]
        ps = request.POST["password"]

        cursor1 = connection.cursor()
        sql1 = "SELECT EMAIL_ADD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor1.execute(sql1, [mail])
        result1 = cursor1.fetchall()
        cursor1.close()

        if (result1):
            print('1')
            msg = "This E-mail ID is already registered."
            return render(request, 'registration.html', {"status": msg})
        else:
            print('2')
            cursor2 = connection.cursor()
            sql2 = "SELECT NID_NO FROM R_USER WHERE NID_NO=%s;"
            cursor2.execute(sql2, [nid])
            result2 = cursor2.fetchall()
            cursor2.close()

            if(result2):
                print('3')
                msg = "This NID number is already registered."
                return render(request, 'registration.html', {"status": msg})
            else:
                print('4')
                cursor3 = connection.cursor()
                sql3 = "SELECT CONTACT_NO FROM R_USER WHERE CONTACT_NO='+880'||%s;"
                cursor3.execute(sql3, [contact])
                result3 = cursor3.fetchall()
                cursor3.close()

                if(result3):
                    print('5')
                    msg = "This contact number is already registered."
                    return render(request, 'registration.html', {"status": msg})
                else:
                    print('6')
                    pw_hash = make_pw_hash(ps)
                    print(pw_hash)

                    # f = open("info.txt", "a+")
                    # f.write(mail+" "+ps)
                    # f.write("\n")
                    # f.close()

                    cursor = connection.cursor()
                    sql = "INSERT INTO R_USER VALUES(NVL((SELECT MAX(USER_ID)+1 FROM R_USER),1),%s,%s,%s,TO_DATE(%s,'YYYY-MM-DD'),CONCAT('+880',%s),%s,%s,%s,%s,%s,%s,%s);"
                    cursor.execute(sql, [
                                   pw_hash, first, last, dob, contact, gender, mail, nid, house, road, zip, city])
                    # result = cursor.fetchall()
                    cursor.close()
                    fullname = first+" "+last
                    return redirect("/login" + "?user=" + fullname)
                    # return render(request, 'login.html')
    return render(request, 'registration.html')


def contactus(request):
    return render(request, 'contactus.html', None)
