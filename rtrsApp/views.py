import decimal
import os
import sys
import twilio
import random
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import hashlib
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import datetime
from django.db import connection
from django.http import HttpResponse
from django.views.generic import View
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from random import randint

from xhtml2pdf import pisa

auth_token = ''

def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
    return False


def changepass(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if(house):
        if(road):
            if(zip):
                address = "House no: "+house+", Road no: "+road+", "+city+"-"+zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    request.session["pnr"] = pnr

    if request.method == "POST":
        ps = request.POST["pass"]
        newps = request.POST["newpass"]
        mail = request.session.get('usermail')
        cursor = connection.cursor()
        sql = "SELECT PASSWORD FROM R_USER WHERE EMAIL_ADD=%s;"
        cursor.execute(sql, [mail])
        result = cursor.fetchall()
        cursor.close()

        for r in result:
            dbps = r[0]
        if (check_pw_hash(ps, dbps)):
            newps_hash = make_pw_hash(newps)

            f = open("info.txt", "a+")
            f.write(mail + " " + newps)
            f.write("\n")
            f.close()
            cursor1 = connection.cursor()
            sql1 = "UPDATE R_USER SET  PASSWORD= %s WHERE EMAIL_ADD=%s;"
            cursor1.execute(sql1, [newps_hash, mail])
            cursor1.close()
            response = "Password successfully updated. "
            return render(request, "changepass.html", {"statusgreen": response, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid})

        else:
            response = "Current password does not match. Try Again!"
            print(response + fullname+mail+address+contact+pnr+nid)
            return render(request, "changepass.html", {"statusred": response, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid})

    return render(request, 'changepass.html', {"fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid})


def changemail(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    hashps = request.session.get('password')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    request.session["pnr"] = pnr
    if request.method == "POST" and 'btn1' in request.POST:
        verification = randint(100000, 999999)
        request.session['veri'] = str(verification)
        currentmail = request.POST["currentmail"]
        out = ""
        newmail = request.POST["newmail"]
        cursor1 = connection.cursor()
        sql = "SELECT EMAIL_ADD FROM R_USER WHERE EMAIL_ADD = %s"
        result = cursor1.execute(sql, [newmail])
        temp = ""
        for r in result:
            temp = r[0]
        if(temp != ""):
            msg = "There is already an account registered with the given new e-mail."
            return render(request, 'changemail.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid})
        request.session['newmail'] = newmail
        usermail = request.session.get('usermail')
        print("\n\n\nCurrentMail: ",currentmail, " usermail: ", usermail)
        if (currentmail == usermail):
            # verification = randint(100000, 999999)
            # request.session['veri']=str(verification)
            #print(str(verification))
            first = request.session.get('first')
            first = first.capitalize()
            last = request.session.get('last')
            last = last.capitalize()
            full = first + ' ' + last
            #mail = newmail
            template = render_to_string('verificationemmail.html', {"name": full, 'code': str(verification)})
            email = EmailMessage(
                'Verification code for changing email address',
                template,
                settings.EMAIL_HOST_USER,
                [newmail],
            )
            email.fail_silently = False
            email.send()
            request.session['mailflag'] = "ok"
        else:
            msg = "Current e-mail does not match. Try Again!"
            return render(request, 'changemail.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid})

    if request.method == "POST" and 'btn3' in request.POST:
        flag = request.session.get('mailflag')
        if flag == "":
            msg = "Click 'Send Verification Code' first to get a verification code."
            return render(request, 'changemail.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid, })
        code = request.POST["otpin"]
        print(code)
        print(request.session.get('veri'))
        ps = request.POST["password"]
        ps = make_pw_hash(ps)
        if ps != hashps:
            #print('here1')
            msg = "Password does not match. Try Again!"
            return render(request, 'changemail.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid})
        if code != request.session.get('veri'):
            #print('here2')
            msg = "Verification code does not match. Try again!."
            return render(request, 'changemail.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid})
        uid = request.session.get('user_id')
        newmail = request.session.get('newmail')
        cursor = connection.cursor()
        sql = "UPDATE R_USER SET EMAIL_ADD=%s WHERE USER_ID=TO_NUMBER(%s);"
        cursor.execute(sql, [newmail, uid])
        cursor.close()
        request.session['usermail'] = newmail
        mail = request.session.get('usermail')
        msg = "E-mail successfully updated."
        print('here3')
        return render(request, 'changemail.html',
                      {"statusgreen": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                       "pnr": pnr, "nid": nid})

    return render(request, 'changemail.html', {"fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid})


def changenum(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    hashps = request.session.get('password')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    request.session["pnr"] = pnr

    if request.method == "POST" and 'btn1' in request.POST:
        otp = random.randint(1000, 9999)
        request.session["otp"] = str(otp)
        num1 = request.POST["num1"]
        num2 = request.POST["num2"]
        number1 = '+880'+str(num1)
        number2 = '+880'+str(num2)
        out = ""
        cursor1 = connection.cursor()
        sql = "SELECT CONTACT_NO FROM R_USER WHERE CONTACT_NO = %s"
        result = cursor1.execute(sql, [number2])
        # cursor1.close()
        temp = ""
        for r in result:
            temp = r[0]
        print(temp)
        if (temp != ""):
            msg = "There is already an account registered with this number."
            return render(request, 'changenum.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid, "password": hashps})
        dbnum = request.session.get('contact')
        if number1 != dbnum:
            msg = "Current number does not match. Try again! "
            return render(request, 'changenum.html', {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid, "password": hashps})
        request.session["tempnum"] = str(num2)
        request.session["numflag"] = "done"
        print("otp= " + str(otp))
        account_sid = 'ACb362c2986bb8893509067b2afc07aa01'
        # auth_token = ''
        client = Client(account_sid, auth_token)

        try:
            message = client.messages \
                .create(
                    body='Your OTP is '+str(otp),
                    from_='+13854628374',
                    to='+880'+num2
                )

            print(message.sid)
        except TwilioRestException as e:
            msg = "Could Not Send SMS.Try Again Later!"
            return render(request, 'changenum.html',
                          {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid, "password": hashps})

    if request.method == "POST" and 'btn3' in request.POST:
        flag = request.session.get('numflag')
        if flag == "":
            msg = "Click 'Send Verification Code' first to get a verification code."
            return render(request, 'changenum.html', {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid, "password": hashps})
        vcode = request.POST["otpin"]
        ps = request.POST["password"]
        ps = make_pw_hash(ps)
        if ps != hashps:
            msg = "Password does not match. Try again!"
            return render(request, 'changenum.html', {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid, "password": hashps})
        uid = request.session.get('user_id')
        tempnum = request.session.get('tempnum')
        otp = request.session.get('otp')
        if vcode == str(otp):
            newnum = '+880'+tempnum
            cursor = connection.cursor()
            sql = "UPDATE R_USER SET CONTACT_NO=%s WHERE USER_ID=TO_NUMBER(%s);"
            cursor.execute(sql, [newnum, uid])
            cursor.close()
            request.session["contact"] = newnum
            contact = request.session.get('contact')
            slice_object = slice(4, 14, 1)
            pnr = contact[slice_object]
            request.session["pnr"] = pnr
            msg = "Contact number successfully updated."
            return render(request, 'changenum.html',
                          {"statusgreen": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact,
                           "pnr": pnr, "nid": nid, "password": hashps})
        else:
            print("otp milena")
            msg = "Password does not match. Try again!"
            return render(request, 'changenum.html', {"statusred": msg, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid, "password": hashps})

    return render(request, 'changenum.html', {"fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid, "password": hashps})


def prev(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    request.session["pnr"] = pnr
    id = request.session.get('user_id')
    dtoj = request.session.get('dtoj')
    print(dtoj)
    cursor = connection.cursor()
    sql = "SELECT (SELECT (SELECT T.NAME FROM TRAIN T WHERE T.TRAIN_ID=B.TRAIN_ID) FROM BOOKED_SEAT B GROUP BY B.RESERVATION_ID,B.TRAIN_ID HAVING B.RESERVATION_ID=R.RESERVATION_ID),INITCAP(R.FROM_STATION),INITCAP(R.TO_STATION),TO_CHAR(R.DATE_OF_JOURNEY,'DD-MM-YYYY')  " \
          "FROM RESERVATION R  " \
          "WHERE DATE_OF_JOURNEY < SYSDATE AND R.USER_ID=TO_NUMBER(%s) " \
          "ORDER BY R.DATE_OF_JOURNEY;"
    cursor.execute(sql, [id])
    result = cursor.fetchall()
    dict_result = []
    i = 1
    for r in result:
        trname = r[0]
        fro = r[1]
        to = r[2]
        doj = r[3]
        row = {'sl': i, 'trname': trname, 'from': fro, 'to': to, 'doj': doj}
        dict_result.append(row)
        i = i+1

    return render(request, 'prev.html', {"record": dict_result, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid})


def upcoming(request):
    first = request.session.get('first')
    last = request.session.get('last')
    mail = request.session.get('usermail')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    contact = request.session.get('contact')
    nid = request.session.get('nid')
    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    request.session["pnr"] = pnr
    
    
    # cursor0 = connection.cursor()
    # sql0 = "SELECT TT.DEPARTURE_TIME" \
    #        "FROM TRAIN_TIMETABLE TT ;"
    # cursor0.execute(sql0, [id, fro])
    # result0 = cursor0.fetchall()
    # cursor0.close()
    # for r in result0:
    #     request.session["dep_time"] = r[0]
    # t = request.session.get('dep_time')+':00'
    # # txt = "banana"
    # # txt.rjust(20,'x')
    # # >>>"xxxxxxxxxxxxxxbanana"
    # t = (t.rjust(8, '0'))
    # print(request.session.get('doj')+' '+t)
    # # date + time = dtoj
    # request.session["dtoj"] = request.session.get('doj')+' '+t
    # dtoj = request.session.get('dtoj')
    # print("\n\n\n\n", doj)
    # print("\n\n\n\n", id)
    
    id = request.session.get('user_id')
    cursor = connection.cursor()
    sql = "SELECT (SELECT (SELECT T.NAME FROM TRAIN T WHERE T.TRAIN_ID=B.TRAIN_ID) FROM BOOKED_SEAT B GROUP BY B.RESERVATION_ID,B.TRAIN_ID HAVING B.RESERVATION_ID=R.RESERVATION_ID),INITCAP(R.FROM_STATION),INITCAP(R.TO_STATION),TO_CHAR(R.DATE_OF_RESERVATION,'HH24:MI , DD-MM-YYYY'),TO_CHAR(R.DATE_OF_JOURNEY,'HH24:MI , DD-MM-YYYY') " \
          "FROM RESERVATION R " \
          "WHERE DATE_OF_JOURNEY > SYSDATE AND R.USER_ID=TO_NUMBER(%s) " \
          "ORDER BY R.DATE_OF_JOURNEY;"
    cursor.execute(sql, [id])
    result = cursor.fetchall()
    dict_result = []
    i = 1
    for r in result:
        trname = r[0]
        fro = r[1]
        to = r[2]
        dor = r[3]
        doj = r[4]
        row = {'sl': i, 'trname': trname, 'from': fro,
               'to': to, 'dor': dor, 'doj': doj}
        dict_result.append(row)
        i = i + 1

    return render(request, 'upcoming.html', {"record": dict_result, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr, "nid": nid})

def updateinfo(request):
    if request.session.get('is_logged_in') != "1":
        return redirect("/login" + "?notdash_logged_in=" + str(0))
    request.session["numflag"] = ""
    request.session["mailflag"] = ""
    mail = request.session.get('usermail')
    contact = request.session.get('contact')
    first = request.session.get('first')
    last = request.session.get('last')
    dob = request.session.get('dob')
    gender = request.session.get('gender')
    nid = request.session.get('nid')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    dob = dob[0:10]
    print("\n\nDOB: ", dob)

    fullname = first + " " + last
    address = ""
    if (house):
        if (road):
            if (zip):
                address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", Road no: " + road + ", " + city
        else:
            if (zip):
                address = "House no: " + house + ", " + city + "-" + zip
            else:
                address = "House no: " + house + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + road + ", " + city + "-" + zip

            else:
                address = "Road no: " + road + ", " + city

        else:
            if (zip):
                address = city + "-" + zip

            else:
                address = city
    slice_object = slice(4, 14, 1)
    pnr = contact[slice_object]
    request.session["pnr"] = pnr
    #return render(request, 'updateinfo.html',{"first":first,"last":last,"dob":dob,"gender":gender,"nid":nid,"house":house,"road":road,"zip":zip,"city":city,"fullname":fullname,"mail":mail,"address":address,"contact":contact,"pnr":pnr})
    if request.method == "POST":
        first = request.POST["first"]
        last = request.POST["last"]
        dob = request.POST["dob"]
        request.session["dob"] = dob
        gender = request.POST["gender"]
        request.session["gender"] = gender.upper()
        nid = request.POST["nid"]
        request.session["nid"] = nid
        house = request.POST["house"]
        request.session["house"] = house.upper()
        road = request.POST["road"]
        request.session["road"] = road.upper()
        zip = request.POST["zip"]
        request.session["zip"] = zip.upper()
        city = request.POST["city"]
        mail = request.session.get('usermail')
        print(request.POST)
        cursor = connection.cursor()
        sql = "UPDATE R_USER SET  FIRST_NAME=%s,LAST_NAME=%s,DOB=TO_DATE(%s,'YYYY-MM-DD'),GENDER=%s,NID_NO=%s,HOUSE_NO=%s,ROAD_NO=%s,ZIP_CODE=%s,CITY=%s WHERE EMAIL_ADD=%s;"
        cursor.execute(sql, [first, last, dob, gender,
                       nid, house, road, zip, city, mail])
        cursor.close()
        first = first.upper()
        request.session["first"] = first
        last = last.upper()
        request.session["last"] = last
        city = city.upper()
        request.session["city"] = city
        mail = request.session.get('usermail')
        contact = request.session.get('contact')
        first = request.session.get('first')
        last = request.session.get('last')
        dob = request.session.get('dob')
        gender = request.session.get('gender')
        nid = request.session.get('nid')
        house = request.session.get('house')
        road = request.session.get('road')
        zip = request.session.get('zip')
        city = request.session.get('city')
        dob = dob[0:10]
        print(dob)

        fullname = first + " " + last
        address = ""
        if (house):
            if (road):
                if (zip):
                    address = "House no: " + house + ", Road no: " + road + ", " + city + "-" + zip
                else:
                    address = "House no: " + house + ", Road no: " + road + ", " + city
            else:
                if (zip):
                    address = "House no: " + house + ", " + city + "-" + zip
                else:
                    address = "House no: " + house + ", " + city
        else:
            if (road):
                if (zip):
                    address = "Road no: " + road + ", " + city + "-" + zip

                else:
                    address = "Road no: " + road + ", " + city

            else:
                if (zip):
                    address = city + "-" + zip

                else:
                    address = city
        slice_object = slice(4, 14, 1)
        # slice(start, end, step)
        pnr = contact[slice_object]
        request.session["pnr"] = pnr
        response = 'Profile updated successfully'
        return render(request, 'updateinfo.html', {"status": response, "first": first, "last": last, "dob": dob, "gender": gender, "nid": nid, "house": house, "road": road, "zip": zip, "city": city, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr})

    else:
        first = request.session.get('first')
        last = request.session.get('last')
        dob = request.session.get('dob')
        gender = request.session.get('gender')
        gender = gender.capitalize()
        nid = request.session.get('nid')
        house = request.session.get('house')
        road = request.session.get('road')
        zip = request.session.get('zip')
        city = request.session.get('city')
        dob = dob[0:10]
        print(dob)
        return render(request, 'updateinfo.html', {"first": first, "last": last, "dob": dob, "gender": gender, "nid": nid, "house": house, "road": road, "zip": zip, "city": city, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr})

    # return render(request, 'updateinfo.html',
    #               {"first": first, "last": last, "dob": dob, "gender": gender, "nid": nid, "house": house, "road": road, "zip": zip, "city": city, "fullname": fullname, "mail": mail, "address": address, "contact": contact, "pnr": pnr})

def card(request):
    amount = request.session.get('cost')
    cursor2 = connection.cursor()
    sql2 = " SELECT TO_CHAR(SYSDATE,'YYYY-MM-DD') FROM DUAL;"
    cursor2.execute(sql2)
    result2 = cursor2.fetchall()
    cursor2.close()
    for r in result2:
        min_date = r[0]
    if request.method == "POST":

        cardnumber = request.POST["cardnumber"]
        name = request.POST["name"]
        cvv = request.POST["cvv"]
        date = request.POST["date"]
        # cursor5 = connection.cursor()
        # # flag = cursor5.callfunc('CHECKEXP', int, [date])
        # cursor5.close()
        # print(flag)
        # if flag == 1:
        #     return redirect("/card_payment" + "?date=" + str(1))
        # cursor=connection.cursor()
        # sql="INSERT INTO PAYMENT VALUES(NVL((SELECT MAX(PAYMENT_ID)+1 FROM PAYMENT),1),%s,SYSDATE);"
        # cursor.execute(sql,[amount])
        # cursor.close()

        doj = request.session.get('doj')
        doj = str(doj)
        dtoj = request.session.get('dtoj')
        dtoj = str(dtoj)
        print(dtoj)
        tot = request.session.get('total_seats')
        adult = request.session.get('adult')
        child = request.session.get('child')
        cls = request.session.get('class')
        fro = request.session.get('from')
        to = request.session.get('to')
        tr = request.session.get('train_id')
        id = request.session.get('user_id')
        cursor2 = connection.cursor()
        sql2 = "INSERT INTO RESERVATION VALUES(NVL((SELECT (MAX(RESERVATION_ID)+1) FROM RESERVATION),1),SYSDATE,TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),TO_NUMBER(%s),TO_NUMBER(%s),%s,%s,%s,TO_NUMBER(%s));"
        cursor2.execute(sql2, [dtoj, adult, child, cls, fro, to, id])
        cursor2.close()
        cursor1 = connection.cursor()
        sql1 = "INSERT INTO CARD VALUES(UPPER(%s),%s,TO_DATE(%s,'YYYY-MM-DD'),%s,NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1));"
        cursor1.execute(sql1, [name, cardnumber, date, cvv])
        cursor1.close()
        seat_nos = request.session.get('seat_nos')
        seat_list = seat_nos.split()
        cursor3 = connection.cursor()
        for s in seat_list:
            seat = str(s)
            sql3 = "INSERT INTO BOOKED_SEAT VALUES(TO_NUMBER(%s),TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),%s,NVL((SELECT (MAX(RESERVATION_ID)) FROM RESERVATION),1), TO_NUMBER(%s));"
            cursor3.execute(sql3, [seat, dtoj, cls, tr])
        cursor3.close()

        cursor4 = connection.cursor()
        sql4 = " SELECT TO_CHAR(SYSDATE,'DD-MM-YYYY'),TO_CHAR(SYSDATE,'HH24:MI') FROM DUAL;"
        cursor4.execute(sql4)
        result4 = cursor4.fetchall()
        cursor4.close()

        for r in result4:
            idate = r[0]
            itime = r[1]
        request.session["idate"] = idate
        request.session["itime"] = itime

        return redirect("/successful")
        # print(request.POST);

    return render(request, 'card_payment.html', {'amount': amount, 'min_date': min_date})


def nexus(request):
    amount = request.session.get('cost')
    if request.method == "POST":

        cardnumber = request.POST["cardnumber"]
        name = request.POST["name"]
        pin = request.POST["pin"]
        # cursor = connection.cursor()
        # sql = "INSERT INTO PAYMENT VALUES(NVL((SELECT MAX(PAYMENT_ID)+1 FROM PAYMENT),1),%s,SYSDATE);"
        # cursor.execute(sql, [amount])
        # cursor.close()

        doj = request.session.get('doj')
        doj = str(doj)
        dtoj = request.session.get('dtoj')
        dtoj = str(dtoj)
        print(dtoj)
        tot = request.session.get('total_seats')
        cls = request.session.get('class')
        fro = request.session.get('from')
        to = request.session.get('to')
        adult = request.session.get('adult')
        child = request.session.get('child')
        tr = request.session.get('train_id')
        id = request.session.get('user_id')
        cursor2 = connection.cursor()
        sql2 = "INSERT INTO RESERVATION VALUES(NVL((SELECT (MAX(RESERVATION_ID)+1) FROM RESERVATION),1),SYSDATE,TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),TO_NUMBER(%s),TO_NUMBER(%s),%s,%s,%s,TO_NUMBER(%s));"
        cursor2.execute(sql2, [dtoj, adult, child, cls, fro, to, id])
        cursor2.close()
        cursor1 = connection.cursor()
        sql1 = "INSERT INTO NEXUSPAY VALUES(UPPER(%s),%s,%s,NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1));"
        cursor1.execute(sql1, [name, cardnumber, pin])
        cursor1.close()
        seat_nos = request.session.get('seat_nos')
        seat_list = seat_nos.split()
        cursor3 = connection.cursor()
        for s in seat_list:
            seat = str(s)
            sql3 = "INSERT INTO BOOKED_SEAT VALUES(TO_NUMBER(%s),TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),%s,NVL((SELECT (MAX(RESERVATION_ID)) FROM RESERVATION),1), TO_NUMBER(%s));"
            cursor3.execute(sql3, [seat, dtoj, cls, tr])
        cursor3.close()

        cursor4 = connection.cursor()
        sql4 = " SELECT TO_CHAR(SYSDATE,'DD-MM-YYYY'),TO_CHAR(SYSDATE,'HH24:MI') FROM DUAL;"
        cursor4.execute(sql4)
        result4 = cursor4.fetchall()
        cursor4.close()

        for r in result4:
            idate = r[0]
            itime = r[1]
        request.session["idate"] = idate
        request.session["itime"] = itime

        return redirect("/successful")
    return render(request, 'nexus_payment.html', {'amount': amount})


# def render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html  = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None

# def pdfforemail(request):
#    #all_student = Students.objects.all()
#     first = request.session.get('first').lower()
#     first = first.capitalize()
#     last = request.session.get('last').lower()
#     last = last.capitalize()
#     fullname = first+' '+last
#     # idate and itime are reservation date and time
#     idate = request.session.get('idate')
#     itime = request.session.get('itime')
#     issue = idate+' '+itime
#     doj = request.session.get('doj')
#     doj = str(doj)
#     # converting year month date to date month year
#     doj = datetime.datetime.strptime(doj, '%Y-%m-%d').strftime('%d-%m-%Y')
#     doj = str(doj)
#     dtime = request.session.get('dep_time')
#     journey = doj + ' '+dtime
#     trid = request.session.get('train_id')
#     trname = request.session.get('train_name')
#     train = '('+trid+') '+trname
#     fro = request.session.get('from')
#     fro = fro.capitalize()
#     to = request.session.get('to')
#     to = to.capitalize()
#     clas = request.session.get('class')
#     clas = clas.capitalize()
#     coach = 'Uma'
#     range = request.session.get('seat_nos')
#     tot = request.session.get('total_seats')
#     adult = request.session.get('adult')
#     child = request.session.get('child')
#     fare = 'BDT ' + str(request.session.get('cost'))
#     vat = 'BDT ' + str(request.session.get('vat'))
#     minusfare = 'BDT ' + \
#         str(int((int(request.session.get('cost'))-int(request.session.get('vat')))))
#     last_time = request.session.get('last_time')
#     collect = doj + ' '+last_time
#     pnr = request.session.get('pnr')
#     data = {'fullname': fullname, 'issue': issue, 'journey': journey, 'train': train, 'from': fro, 'to': to, 'class': clas, 'coach': coach,
#             'range': range, 'total': tot, 'adult': adult, 'child': child, 'fare': fare, 'vat': vat, 'minusfare': minusfare, 'collect': collect, 'pnr': pnr}
#     template = get_template("ticket.html")
#     # data_p = template.render(data)
#     pdf = render_to_pdf('ticket.html', data)
#     if pdf:
#       response = HttpResponse(pdf,content_type='application/pdf')
#       filename = "rtrs_eticket%s.pdf" %(data['fullname'])
#       content = "inline; filename='%s'" %(filename)
#       response['Content-Disposition'] = content
#       return response

#     return HttpResponse("Not Found")
    # response = BytesIO()
    # pdfPage = pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")), response)
    # if not pdfPage.err:
    #     return  content_type="application/pdf"
    # else:
    #     return HttpResponse("Error Generating PDF")



def pdf(request):
   #all_student = Students.objects.all()
    first = request.session.get('first').lower()
    first = first.capitalize()
    last = request.session.get('last').lower()
    last = last.capitalize()
    fullname = first+' '+last
    # idate and itime are reservation date and time
    idate = request.session.get('idate')
    itime = request.session.get('itime')
    issue = idate+' '+itime
    doj = request.session.get('doj')
    doj = str(doj)
    # converting year month date to date month year
    doj = datetime.datetime.strptime(doj, '%Y-%m-%d').strftime('%d-%m-%Y')
    doj = str(doj)
    dtime = request.session.get('dep_time')
    journey = doj + ' '+dtime
    trid = request.session.get('train_id')
    trname = request.session.get('train_name')
    train = '('+trid+') '+trname
    fro = request.session.get('from')
    fro = fro.capitalize()
    to = request.session.get('to')
    to = to.capitalize()
    clas = request.session.get('class')
    clas = clas.capitalize()
    coach = 'Uma'
    range = request.session.get('seat_nos')
    tot = request.session.get('total_seats')
    adult = request.session.get('adult')
    child = request.session.get('child')
    fare = 'BDT ' + str(request.session.get('cost'))
    vat = 'BDT ' + str(request.session.get('vat'))
    minusfare = 'BDT ' + \
        str(int((int(request.session.get('cost'))-int(request.session.get('vat')))))
    last_time = request.session.get('last_time')
    collect = doj + ' '+last_time
    pnr = request.session.get('pnr')
    data = {'fullname': fullname, 'issue': issue, 'journey': journey, 'train': train, 'from': fro, 'to': to, 'class': clas, 'coach': coach,
            'range': range, 'total': tot, 'adult': adult, 'child': child, 'fare': fare, 'vat': vat, 'minusfare': minusfare, 'collect': collect, 'pnr': pnr}
    template = get_template("ticket.html")
    data_p = template.render(data)
    #pdf = render_to_pdf('ticket.html', data)
    response = BytesIO()
    pdfPage = pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")), response)
    if not pdfPage.err:
        return HttpResponse(response.getvalue(), content_type="application/pdf")
    else:
        return HttpResponse("Error Generating PDF")


def rocket(request):
    amount = request.session.get('cost')
    if request.method == "POST" and 'btn1' in request.POST:
        name = request.POST["name"]
        request.session["paymentname"] = name
        ps = request.POST["password"]
        request.session["paymentpass"] = ps
        request.session["paymentflag"] = "done"
        otp = random.randint(1000, 9999)
        request.session["otp"] = str(otp)
        print("otp= "+str(otp))
        account_sid = 'ACb362c2986bb8893509067b2afc07aa01'

        client = Client(account_sid, auth_token)
        try:
            message = client.messages \
                .create(
                    body='Your OTP is '+str(otp),
                    from_='+13854628374',
                    to='+88'+name
                )

            print(message.sid)
        except TwilioRestException as e:
            msg = "Could Not Send SMS.Try Again Later!"
            return render(request, 'rocket_payment.html', {"status": msg, 'amount': amount})

    if request.method == "POST" and 'btn3' in request.POST:
        flag = request.session.get('paymentflag')
        if flag == "":
            msg = "Click 'Send Verification Code' first to get an OTP."
            return render(request, 'rocket_payment.html', {"status": msg, 'amount': amount})
        vcode = request.POST["otpin"]
        name = request.session.get('paymentname')
        ps = request.session.get('paymentpass')
        otp = request.session.get('otp')
        if vcode == str(otp):
            # cursor = connection.cursor()
            # sql = "INSERT INTO PAYMENT VALUES(NVL((SELECT (MAX(PAYMENT_ID)+1) FROM PAYMENT),1),%s,SYSDATE);"
            # cursor.execute(sql, [amount])
            # cursor.close()

            doj = request.session.get('doj')
            doj = str(doj)
            print(doj)
            dtoj = request.session.get('dtoj')
            dtoj = str(dtoj)
            print(dtoj)
            tot = request.session.get('total_seats')
            adult = request.session.get('adult')
            child = request.session.get('child')
            cls = request.session.get('class')
            fro = request.session.get('from')
            to = request.session.get('to')
            tr = request.session.get('train_id')
            id = request.session.get('user_id')
            cursor2 = connection.cursor()
            sql2 = "INSERT INTO RESERVATION VALUES(NVL((SELECT (MAX(RESERVATION_ID)+1) FROM RESERVATION),1),SYSDATE,TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),TO_NUMBER(%s),TO_NUMBER(%s),%s,%s,%s,TO_NUMBER(%s));"
            cursor2.execute(sql2, [dtoj, adult, child, cls, fro, to, id])
            cursor2.close()
            cursor1 = connection.cursor()
            # print("payment e dhukse")
            sql1 = "INSERT INTO MOBILE_BANKING VALUES(TO_NUMBER(%s),TO_NUMBER(%s),TO_NUMBER(%s), NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1));"
            cursor1.execute(sql1, [name, vcode, ps])
            cursor1.close()
            seat_nos = request.session.get('seat_nos')
            seat_list = seat_nos.split()
            cursor3 = connection.cursor()
            for s in seat_list:
                seat = str(s)
                sql3 = "INSERT INTO BOOKED_SEAT VALUES(TO_NUMBER(%s),TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),%s,NVL((SELECT (MAX(RESERVATION_ID)) FROM RESERVATION),1), TO_NUMBER(%s));"
                cursor3.execute(sql3, [seat, dtoj, cls, tr])
            cursor3.close()

            cursor4 = connection.cursor()
            sql4 = " SELECT TO_CHAR(SYSDATE,'DD-MM-YYYY'),TO_CHAR(SYSDATE,'HH24:MI') FROM DUAL;"
            cursor4.execute(sql4)
            result4 = cursor4.fetchall()
            cursor4.close()

            for r in result4:
                idate = r[0]
                itime = r[1]
            request.session["idate"] = idate
            request.session["itime"] = itime

            return redirect("/successful")
        if vcode != "" and vcode != str(otp):
            print("otp milena")
            msg = "Wrong OTP Entered."
            return render(request, 'rocket_payment.html', {"status": msg, 'amount': amount})

    return render(request, 'rocket_payment.html', {'amount': amount})


def successful(request):
    # first = request.session.get('first')
    # # first = first.capitalize()
    # last = request.session.get('last')
    # # last = last.capitalize()
    # full = first+' '+last
    
    first = request.session.get('first').lower()
    first = first.capitalize()
    last = request.session.get('last').lower()
    last = last.capitalize()
    full = first+' '+last
    # idate and itime are reservation date and time
    idate = request.session.get('idate')
    itime = request.session.get('itime')
    issue = idate+' '+itime
    doj = request.session.get('doj')
    doj = str(doj)
    # converting year month date to date month year
    doj = datetime.datetime.strptime(doj, '%Y-%m-%d').strftime('%d-%m-%Y')
    doj = str(doj)
    dtime = request.session.get('dep_time')
    journey = doj + ' '+dtime
    trid = request.session.get('train_id')
    trname = request.session.get('train_name')
    train = '('+trid+') '+trname
    fro = request.session.get('from')
    fro = fro.capitalize()
    to = request.session.get('to')
    to = to.capitalize()
    clas = request.session.get('class')
    clas = clas.capitalize()
    coach = 'Uma'
    range = request.session.get('seat_nos')
    tot = request.session.get('total_seats')
    adult = request.session.get('adult')
    child = request.session.get('child')
    fare = 'BDT ' + str(request.session.get('cost'))
    vat = 'BDT ' + str(request.session.get('vat'))
    minusfare = 'BDT ' + \
        str(int((int(request.session.get('cost'))-int(request.session.get('vat')))))
    last_time = request.session.get('last_time')
    collect = doj + ' '+last_time
    pnr = request.session.get('pnr')
    data = {'fullname': full, 'issue': issue, 'journey': journey, 'train': train, 'from': fro, 'to': to, 'class': clas, 'coach': coach,
            'range': range, 'total': tot, 'adult': adult, 'child': child, 'fare': fare, 'vat': vat, 'minusfare': minusfare, 'collect': collect, 'pnr': pnr}
    template = get_template("ticket.html")
    data_p = template.render(data)
    #pdf = render_to_pdf('ticket.html', data)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")), response)
    pdf= response.getvalue()
    filename = "rtrs_eticket"+journey +".pdf"
    
    mail = request.session.get('usermail')
    # print(mail)
    
    template = render_to_string('email.html', {"name": full})
    email = EmailMessage(
        'Confirmation of e-ticket booking in RTRS',
        template,
        settings.EMAIL_HOST_USER,
        [mail],
    )
    # fail_silently = False will raise an error if email is not sent
    email.fail_silently = False
    email.attach(filename, pdf, 'application/pdf')
    email.send()
    train_id = request.session.get('train_id')
    cursor = connection.cursor()
    sql = "SELECT NAME FROM TRAIN WHERE TRAIN_ID=%s;"
    cursor.execute(sql, [train_id])
    result = cursor.fetchall()
    cursor.close()
    name = ""
    for r in result:
        name = r[0]

    return render(request, 'successful.html', {"name": name, "train_id": train_id, "total_seats": request.session.get('total_seats'),
                                               "amount": request.session.get('cost'), "from": request.session.get('from'), "to": request.session.get('to'), "class": request.session.get('class')})


def bkash(request):
    amount = request.session.get('cost')
    if request.method == "POST" and 'btn1' in request.POST:
        name = request.POST["name"]
        # name represents phone number
        request.session["paymentname"] = name
        ps = request.POST["password"]
        request.session["paymentpass"] = ps
        request.session["paymentflag"] = "done"
        otp = random.randint(1000, 9999)
        request.session["otp"] = str(otp)
        print("\n\n\n\n\otp= "+str(otp)+"\n\n\n\\n\n")
        account_sid = 'ACb362c2986bb8893509067b2afc07aa01'
        client = Client(account_sid, auth_token)
        try:
            message = client.messages \
                .create(
                    body='Your OTP is '+str(otp),
                    from_='+13854628374',
                    to='+88'+name
                )

            print(message.sid)
        except TwilioRestException as e:
            msg = "Could Not Send SMS.Try Again Later!"
            return render(request, 'bkash_payment.html', {"status": msg, 'amount': amount})

    if request.method == "POST" and 'btn3' in request.POST:
        flag = request.session.get('paymentflag')
        if flag == "":
            msg = "Click 'Send Verification Code' first to get an OTP."
            return render(request, 'bkash_payment.html', {"status": msg, 'amount': amount})
        vcode = request.POST["otpin"]
        name = request.session.get('paymentname')
        ps = request.session.get('paymentpass')
        otp = request.session.get('otp')
        if vcode == str(otp):
            cursor = connection.cursor()
            sql = "INSERT INTO PAYMENT VALUES(NVL((SELECT (MAX(PAYMENT_ID)+1) FROM PAYMENT),1),%s,SYSDATE);"
            cursor.execute(sql, [amount])
            cursor.close()

            doj = request.session.get('doj')
            doj = str(doj)
            dtoj = request.session.get('dtoj')
            dtoj = str(dtoj)
            print(dtoj)
            tot = request.session.get('total_seats')
            adult = request.session.get('adult')
            child = request.session.get('child')
            cls = request.session.get('class')
            fro = request.session.get('from')
            to = request.session.get('to')
            tr = request.session.get('train_id')
            id = request.session.get('user_id')
            cursor2 = connection.cursor()
            print("\n\n\n\n\nID: ", id, "\n\n\n\n")
            sql2 = "INSERT INTO RESERVATION VALUES(NVL((SELECT (MAX(RESERVATION_ID)+1) FROM RESERVATION),1),SYSDATE,TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),TO_NUMBER(%s),TO_NUMBER(%s),%s,%s,%s,TO_NUMBER(%s));"
            cursor2.execute(sql2, [dtoj, adult, child, cls, fro, to, id])
            cursor2.close()
            cursor1 = connection.cursor()
            #print("payment e dhukse")
            sql1 = "INSERT INTO MOBILE_BANKING VALUES(TO_NUMBER(%s),TO_NUMBER(%s),TO_NUMBER(%s), NVL((SELECT MAX(PAYMENT_ID) FROM PAYMENT),1));"
            cursor1.execute(sql1, [name, vcode, ps])
            cursor1.close()
            seat_nos = request.session.get('seat_nos')
            seat_list = seat_nos.split(" ")
            print("seat_list: ", seat_list, "\n\n\n\n\n\n")
            cursor3 = connection.cursor()
            for s in seat_list:
                if s != '':
                    seat = str(s)
                    print(seat)
                    sql3 = "INSERT INTO BOOKED_SEAT VALUES(TO_NUMBER(%s),TO_DATE(%s,'YYYY-MM-DD hh24:mi:ss'),%s,NVL((SELECT (MAX(RESERVATION_ID)) FROM RESERVATION),1), TO_NUMBER(%s));"
                    cursor3.execute(sql3, [seat, dtoj, cls, tr])
            cursor3.close()

            cursor4 = connection.cursor()
            sql4 = "SELECT TO_CHAR(SYSDATE,'DD-MM-YYYY'),TO_CHAR(SYSDATE,'HH24:MI') FROM DUAL;"
            cursor4.execute(sql4)
            result4 = cursor4.fetchall()
            cursor4.close()

            for r in result4:
                idate = r[0]
                itime = r[1]
            request.session["idate"] = idate
            request.session["itime"] = itime

            return redirect("/successful")
        if vcode != "" and vcode != str(otp):
            print("otp milena")
            msg = "Wrong OTP Entered."
            return render(request, 'bkash_payment.html', {"status": msg, 'amount': amount})

    return render(request, 'bkash_payment.html', {'amount': amount})


def payment_selection(request):
    # getting the seat numbers from frontend
    seat_nos = request.GET.get('seat_nos')

    total_seats = request.session.get('total_seats')
    amount = request.session.get('cost')
    request.session["paymentflag"] = ""
    if(seat_nos[0] == 'a'):
        print("\t Auto Seat Selection")
        clas = request.session.get('class')
        train_id = request.session.get('train_id')
        doj = request.session.get('doj')

        cursor = connection.cursor()
        # trunc sudhu date k alada kore datetime theke
        sql = "SELECT SEAT_NO FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND SEAT_CLASS=%s AND TRUNC(DATE_OF_JOURNEY)= TO_DATE(%s,'YYYY-MM-DD');"
        cursor.execute(sql, [train_id, clas, doj])
        result = cursor.fetchall()
        cursor.close()
        booked_seats = []
        for r in result:
            seat_no = r[0]
            booked_seats.append(seat_no)
        if(78 - len(booked_seats) < int(total_seats)):
            return redirect("/" + "?not_enough_seats=" + str(1))
        else:
            seat_nos = ""
            count = 0
            print("\n\n\nBooked seats: ", booked_seats)
            # print("total_seats: ", total_seats)
            for i in range(1, 79):
                if count == int(total_seats):
                    break
                if i not in booked_seats:
                    seat_nos += str(i)+" "
                    count += 1
                    print('Seat: ', i)
                    # print('count: ', count)

        request.session["seat_nos"] = seat_nos
        print("\n\n\n\nSeat nos: "+seat_nos+"\n\n\n")
        return render(request, 'payment selection.html', {'amount': amount})

        # cursor = connection.cursor()
        # out = ""
        # total_seats = int(total_seats)
        # result = cursor.callproc(
        #     'SEATNOS', [total_seats, train_id, clas, doj, out])
        # print(result[4])
        # request.session["seat_nos"] = result[4]
    else:
        print("\t Manual Seat Selection")
        print(total_seats)
        # removing 'b' part came or 0th index from front end in seat_nos string
        seat_nos = seat_nos[1:]
        print(seat_nos)
        id = request.session.get('train_id')
        request.session["seat_nos"] = seat_nos
        seat_list = seat_nos.split()
        print(seat_list)
        if(int(total_seats) != len(seat_list)):
            return redirect("/seat_selection" + "?not_equal=" + id)

        # print(seat_list)
        return render(request, 'payment selection.html', {'amount': amount})



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
    if(request.GET.get('id')):
        id = request.GET.get('id')
    else:
        id = request.GET.get('not_equal')
    request.session["train_id"] = id
    fro = request.session.get('from')
    cursor0 = connection.cursor()
    sql0 = "SELECT (SELECT NAME FROM TRAIN T WHERE T.TRAIN_ID=TT.TRAIN_ID),TT.DEPARTURE_TIME,TO_CHAR(TO_DATE(TT.DEPARTURE_TIME,'HH24:MI')-(1/1440*15),'HH24:MI') " \
           "FROM TRAIN_TIMETABLE TT " \
           "WHERE TT.TRAIN_ID=TO_NUMBER(%s) AND STATION_ID=(SELECT STATION_ID FROM STATION WHERE NAME=%s);"
    cursor0.execute(sql0, [id, fro])
    result0 = cursor0.fetchall()
    cursor0.close()
    for r in result0:
        request.session["train_name"] = r[0]
        request.session["dep_time"] = r[1]
        request.session["last_time"] = r[2]
    t = request.session.get('dep_time')+':00'
    # txt = "banana"
    # txt.rjust(20,'x')
    # >>>"xxxxxxxxxxxxxxbanana"
    t = (t.rjust(8, '0'))
    print(request.session.get('doj')+' '+t)
    # date + time = dtoj
    request.session["dtoj"] = request.session.get('doj')+' '+t
    clas = request.session.get('class')
    adult = request.session.get('adult')
    child = request.session.get('child')
    date = request.session.get('doj')
    fro = request.session.get('from')
    to = request.session.get('to')
    house = request.session.get('house')
    road = request.session.get('road')
    zip = request.session.get('zip')
    city = request.session.get('city')
    doj = request.session.get('doj')
    if (house):
        if (road):
            if (zip):
                address = "House no: " + \
                    str(house) + ", Road no: " + str(road) + \
                    ", " + city + "-" + str(zip)
            else:
                address = "House no: " + \
                    str(house) + ", Road no: " + str(road) + ", " + city
        else:
            if (zip):
                address = "House no: " + \
                    str(house) + ", " + city + "-" + str(zip)
            else:
                address = "House no: " + str(house) + ", " + city
    else:
        if (road):
            if (zip):
                address = "Road no: " + \
                    str(road) + ", " + city + "-" + str(zip)

            else:
                address = "Road no: " + str(road) + ", " + city

        else:
            if (zip):
                address = city + "-" + str(zip)

            else:
                address = city
    cursor = connection.cursor()
    # trunc sudhu date k alada kore datetime theke
    sql = "SELECT SEAT_NO FROM BOOKED_SEAT WHERE TRAIN_ID=%s AND SEAT_CLASS=%s AND TRUNC(DATE_OF_JOURNEY)= TO_DATE(%s,'YYYY-MM-DD');"
    cursor.execute(sql, [id, clas, doj])
    result = cursor.fetchall()
    cursor.close()
    booked_seats = []
    for r in result:
        seat_no = r[0]
        booked_seats.append(seat_no)

    print(booked_seats)
    return render(request, 'seat_selection.html', {'booked_seats': booked_seats, 'from': fro, 'to': to, 'date': date, 'class': clas, 'adult': adult, 'child': child, 'train_name': request.session.get('train_name'), 'cost': request.session.get('cost'),
                                                   'mail': request.session.get('usermail'), 'mobile': request.session.get('contact'), 'full': request.session.get('first')+' '+request.session.get('last'), 'address': address})


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
            account_sid = 'ACb362c2986bb8893509067b2afc07aa01'
            client = Client(account_sid, auth_token)

            try:
                message = client.messages \
                    .create(
                        body='Your OTP for RTRS is ' +
                        str(otp)+' \nRegards\nTeam RTRS',
                        from_='+13854628374',
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
