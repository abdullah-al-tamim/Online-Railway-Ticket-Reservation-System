from django.shortcuts import render, redirect, HttpResponse
from django.db import connection
import hashlib

# Create your views here.


def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
    return False


def homepage(request):
    return render(request, 'search.html', None)


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
