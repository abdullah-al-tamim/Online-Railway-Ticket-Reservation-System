from django.shortcuts import render, redirect, HttpResponse
from django.db import connection
import hashlib

# Create your views here.
def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def homepage(request):
    return render(request, 'search.html', None)


def login(request):
    return render(request, 'login.html', None)


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
                    #return render(request, 'login.html')
    return render(request, 'registration.html')


def contactus(request):
    return render(request, 'contactus.html', None)
