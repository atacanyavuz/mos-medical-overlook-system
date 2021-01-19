from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mos"

app.config["MYSQL_HOST"] = "eu-cdbr-west-03.cleardb.net"
app.config["MYSQL_USER"] = "bcc5cf4a95a727"
app.config["MYSQL_PASSWORD"] = "4877e0cc"
app.config["MYSQL_DB"] = "heroku_ed2c0c5a4f6c53d"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        log_type = request.form["logtype"]

        if(log_type == "doctor"):
            cursor = mysql.connection.cursor()
            sorgu = "Select * From doctors where e_mail = %s"
            result = cursor.execute(sorgu, (email,))

            if result > 0:
                data = cursor.fetchone()
                db_password = data["doctor_password"]
                if password == db_password:
                    flash("You have successfully logged in.", "green")
                    db_doctor_id = data["doctor_id"]
                    db_doctor_admin = data["is_admin"]

                    if db_doctor_admin == b'\x01':
                        db_doctor_admin = True
                    else:
                        db_doctor_admin = False

                    db_doctor_profession = data["profession"]

                    session["logged_in"] = True
                    session["Login_type"] = "Doctor"
                    session["doctor_id"] = db_doctor_id
                    session["is_admin"] = db_doctor_admin
                    session["profession"] = db_doctor_profession

                    return redirect(url_for("index"))
                else:
                    flash("You Entered Your Password Incorrectly.", "red")
                    return redirect(url_for("login"))
            else:
                flash("User not found.", "red")
                return redirect(url_for("login"))

        elif(log_type == "patient"):

            cursor = mysql.connection.cursor()
            sorgu = "Select * From patients where e_mail = %s"
            result = cursor.execute(sorgu, (email,))

            if result > 0:
                data = cursor.fetchone()
                db_password = data["patient_password"]
                if password == db_password :
                    flash("You have successfully logged in.", "green")

                    db_patient_id = data["patient_id"]

                    session["logged_in"] = True
                    session["Login_type"] = "Patient"
                    session["patient_id"] = db_patient_id

                    return redirect(url_for("index"))
                else:
                    flash("You Entered Your Password Incorrectly.", "red")
                    return redirect(url_for("login"))
            else:
                flash("User not found.", "red")
                return redirect(url_for("login"))


    else:
        return render_template("login.html")



#Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/add_admin_doctor", methods=["GET", "POST"])
def add_admin_doctor():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]

        password = request.form["password"]

        age = request.form["age"]
        age = int(age)

        email = request.form["email"]
        phone_num = request.form["phone_num"]
        profession = request.form["profession"]
        hospital = request.form["hospital"]
        is_admin = 1

        cursor = mysql.connection.cursor()
        query = "Select * From doctors where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:      # Böyle bir kullanıcı var. Kayıt işlemi başarısız.
            flash("This e-mail address is used by someone else.", "red")
            return redirect(url_for("add_admin_doctor"))

        else:
            cursor = mysql.connection.cursor()
            query = "Insert into doctors(doctor_password,doctor_name,doctor_surname,age,e_mail,phone_num,profession,hospital, is_admin) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(query, (password, name, surname, age, email, phone_num, profession, hospital, is_admin))
            mysql.connection.commit()
            flash("You Have Successfully Registered.", "green")
            return redirect(url_for("add_admin_doctor"))
    else:
        return render_template("admin_doctor_register.html")




@app.route("/doctor_operation")
def doct_operation():
    return render_template("doct_operation.html")

@app.route("/patient_operation")
def patient_operation():
    return render_template("patient_operation.html")

@app.route("/profile")
def profile():
    if session["Login_type"] == "Doctor":
        doctor_id = session["doctor_id"]

        cursor = mysql.connection.cursor()
        sorgu = "Select * From doctors where doctor_id = %s"
        result = cursor.execute(sorgu, (doctor_id,))
        data = cursor.fetchone()

        name = data["doctor_name"]
        surname = data["doctor_surname"]
        age = data["age"]
        email = data["e_mail"]
        phone_num = data["phone_num"]
        profession = data["profession"]
        hospital = data["hospital"]

        return render_template("profile.html", doctor_name=name, doctor_surname=surname, age=age, email=email, phone_num=phone_num, profession=profession, hospital=hospital)

    elif session["Login_type"] == "Patient":
        patient_id = session["patient_id"]

        cursor = mysql.connection.cursor()
        sorgu = "Select * From patients where patient_id = %s"
        result = cursor.execute(sorgu, (patient_id,))
        data = cursor.fetchone()

        name = data["patient_name"]
        surname = data["patient_surname"]
        age = data["age"]
        email = data["e_mail"]
        address = data["adress"]
        phone_num = data["phone_num"]
        last_checkup = data["last_checkup_date"]
        last_checkup = str(last_checkup)
        last_checkup = last_checkup.split("-")
        date = last_checkup[2]+"."+last_checkup[1]+"."+last_checkup[0]

        doct_id = data["family_doctor_id"]
        cursor = mysql.connection.cursor()
        sorgu = "Select * From doctors where doctor_id = %s"
        result = cursor.execute(sorgu, (doct_id,))
        data = cursor.fetchone()

        doctor_name = data["doctor_name"]
        doctor_surname = data["doctor_surname"]
        doctor = doctor_name + " " +doctor_surname

        return render_template("profile.html", patient_name=name, patient_surname=surname, age=age, email=email, phone_num=phone_num, last_checkup_date=date, family_doctor=doctor, address=address)



@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():           # Not Admin
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]

        password = request.form["password"]

        age = request.form["age"]
        age = int(age)

        email = request.form["email"]
        phone_num = request.form["phone_num"]
        profession = request.form["profession"]
        hospital = request.form["hospital"]
        is_admin = 0

        cursor = mysql.connection.cursor()
        query = "Select * From doctors where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            flash("This e-mail address is used by someone else.", "red")
            return redirect(url_for("add_doctor"))

        else:
            cursor = mysql.connection.cursor()
            query = "Insert into doctors(doctor_password,doctor_name,doctor_surname,age,e_mail,phone_num,profession,hospital, is_admin) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(query, (password, name, surname, age, email, phone_num, profession, hospital, is_admin))
            mysql.connection.commit()
            flash("You Have Successfully Registered.", "green")
            return redirect(url_for("add_doctor"))
    else:
        return render_template("add_doctor.html")


@app.route("/search_doctor_update", methods=["GET", "POST"])
def search_doctor_update():
    if request.method == "POST":
        email = request.form["email"]

        cursor = mysql.connection.cursor()
        query = "Select * From doctors where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            data = cursor.fetchone()
            session["update_doctor_id"] = data["doctor_id"]
            return redirect(url_for("update_doctor"))
        else:
            flash("The doctor with this e-mail address was not found.", "red")
            return redirect(url_for("search_doctor_update"))

    else:
        return render_template("search_doctor_update.html")

@app.route("/update_doctor", methods=["GET", "POST"])
def update_doctor():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]

        password = request.form["password"]

        age = request.form["age"]
        age = int(age)

        email = request.form["email"]
        phone_num = request.form["phone_num"]
        profession = request.form["profession"]
        hospital = request.form["hospital"]

        cursor = mysql.connection.cursor()

        query = "Update doctors Set doctor_password = %s,doctor_name = %s,doctor_surname = %s,age = %s,e_mail = %s,phone_num = %s,profession = %s,hospital = %s where doctor_id = %s"
        result = cursor.execute(query, (password, name, surname, age, email, phone_num, profession, hospital,session["update_doctor_id"]))
        mysql.connection.commit()

        flash("The doctor has been updated successfully.","green")
        return redirect(url_for("search_doctor_update"))


    else:
        cursor = mysql.connection.cursor()
        query = "Select * From doctors where doctor_id = %s"
        result = cursor.execute(query, (session["update_doctor_id"],))
        data = cursor.fetchone()
        return render_template("update_doctor.html", name=data["doctor_name"], surname=data["doctor_surname"], age=data["age"], email=data["e_mail"], phone_num=data["phone_num"], profession=data["profession"], hospital=data["hospital"])

@app.route("/search_doctor_delete", methods=["GET", "POST"])
def search_doctor_delete():
    if request.method == "POST":
        email = request.form["email"]

        cursor = mysql.connection.cursor()
        query = "Select * From doctors where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            data = cursor.fetchone()
            session["delete_doctor_id"] = data["doctor_id"]
            return redirect(url_for("delete_doctor"))
        else:
            flash("The doctor with this e-mail address was not found.", "red")
            return redirect(url_for("search_doctor_delete"))

    else:
        return render_template("search_doctor_delete.html")

@app.route("/delete_doctor", methods=["GET", "POST"])
def delete_doctor():
    if request.method == "POST":

        confirm = request.form["confirm"]

        if confirm == "YES":
            cursor = mysql.connection.cursor()
            query = "Delete From doctors where doctor_id = %s"
            cursor.execute(query, (session["delete_doctor_id"],))
            mysql.connection.commit()

            flash("You successfully deleted.", "green")
            return redirect(url_for("search_doctor_delete"))

        else:
            return redirect(url_for("search_doctor_delete"))

    else:
        return render_template("delete_doctor.html")



@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]

        password = request.form["password"]


        age = request.form["age"]
        age = int(age)

        email = request.form["email"]
        address = request.form["address"]
        phone_num = request.form["phone_num"]
        last_checkup_date = datetime.now()
        last_checkup_date = last_checkup_date.date()
        family_doctor_id = session["doctor_id"]


        cursor = mysql.connection.cursor()
        query = "Select * From patients where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            flash("This e-mail address is used by someone else.", "red")
            return redirect(url_for("add_patient"))

        else:
            cursor = mysql.connection.cursor()
            query = "Insert into patients(patient_password,patient_name,patient_surname,age,e_mail,adress,phone_num,last_checkup_date, family_doctor_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(query, (password, name, surname, age, email, address, phone_num, last_checkup_date, family_doctor_id))
            mysql.connection.commit()
            flash("You Have Successfully Registered.", "green")
            return redirect(url_for("add_patient"))
    else:
        return render_template("add_patient.html")

@app.route("/search_patient_update", methods=["GET", "POST"])
def search_patient_update():
    if request.method == "POST":
        email = request.form["email"]

        cursor = mysql.connection.cursor()
        query = "Select * From patients where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            data = cursor.fetchone()
            session["update_patient_id"] = data["patient_id"]
            return redirect(url_for("update_patient"))
        else:
            flash("The patient with this e-mail address was not found.", "red")
            return redirect(url_for("search_patient_update"))

    else:
        return render_template("search_patient_update.html")

@app.route("/update_patient", methods=["GET", "POST"])
def update_patient():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]

        password = request.form["password"]


        age = request.form["age"]
        age = int(age)

        email = request.form["email"]
        address = request.form["address"]
        phone_num = request.form["phone_num"]



        cursor = mysql.connection.cursor()

        query = "Update patients Set patient_password = %s,patient_name = %s,patient_surname = %s,age = %s,e_mail = %s,phone_num = %s,adress = %s where patient_id = %s"
        result = cursor.execute(query, (password, name, surname, age, email, phone_num, address, session["update_patient_id"]))
        mysql.connection.commit()

        flash("The patient has been updated successfully.","green")
        return redirect(url_for("search_patient_update"))


    else:
        cursor = mysql.connection.cursor()
        query = "Select * From patients where patient_id = %s"
        result = cursor.execute(query, (session["update_patient_id"],))
        data = cursor.fetchone()
        return render_template("update_patient.html", name=data["patient_name"], surname=data["patient_surname"], age=data["age"], email=data["e_mail"], phone_num=data["phone_num"], address=data["adress"])

@app.route("/search_patient_delete", methods=["GET", "POST"])
def search_patient_delete():
    if request.method == "POST":
        email = request.form["email"]

        cursor = mysql.connection.cursor()
        query = "Select * From patients where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            data = cursor.fetchone()
            session["delete_patient_id"] = data["patient_id"]
            return redirect(url_for("delete_patient"))
        else:
            flash("The patient with this e-mail address was not found.", "red")
            return redirect(url_for("search_doctor_delete"))

    else:
        return render_template("search_patient_delete.html")

@app.route("/delete_patient", methods=["GET", "POST"])
def delete_patient():
    if request.method == "POST":

        confirm = request.form["confirm"]

        if confirm == "YES":
            cursor = mysql.connection.cursor()
            query = "Delete From patients where patient_id = %s"
            cursor.execute(query, (session["delete_patient_id"],))
            mysql.connection.commit()

            flash("You successfully deleted.", "green")
            return redirect(url_for("search_patient_delete"))

        else:
            return redirect(url_for("search_patient_delete"))

    else:
        return render_template("delete_patient.html")

@app.route("/my_patients")
def my_patients():
    family_doctor_id = session["doctor_id"]

    cursor = mysql.connection.cursor()
    query = "Select * from patients where family_doctor_id = %s "
    result = cursor.execute(query,(family_doctor_id,))

    if(result == 0):
        flash("No patients were found.","yellow")
        return render_template("my_patients.html")
    else:
        patients = cursor.fetchall()
        return render_template("my_patients.html", my_patients=patients)

@app.route("/find_patient", methods=["GET", "POST"])
def find_patient():
    if request.method == "POST":
        email = request.form["email"]

        cursor = mysql.connection.cursor()
        query = "Select * From patients where e_mail = %s"
        result = cursor.execute(query, (email,))

        if result > 0:
            data = cursor.fetchone()
            session["found_patient"] = data["patient_id"]
            return redirect(url_for("found_patient"))
        else:
            flash("Patient not found.", "red")
            return redirect(url_for("find_patient"))

    else:
        return render_template("find_patient.html")

@app.route("/found_patient")
def found_patient():
    patient_id = session["found_patient"]

    cursor = mysql.connection.cursor()
    sorgu = "Select * From patients where patient_id = %s"
    result = cursor.execute(sorgu, (patient_id,))
    data = cursor.fetchone()

    name = data["patient_name"]
    surname = data["patient_surname"]
    age = data["age"]
    email = data["e_mail"]
    address = data["adress"]
    phone_num = data["phone_num"]
    last_checkup = data["last_checkup_date"]
    last_checkup = str(last_checkup)
    last_checkup = last_checkup.split("-")
    date = last_checkup[2] + "." + last_checkup[1] + "." + last_checkup[0]

    doct_id = data["family_doctor_id"]
    cursor = mysql.connection.cursor()
    sorgu = "Select * From doctors where doctor_id = %s"
    result = cursor.execute(sorgu, (doct_id,))
    data = cursor.fetchone()

    doctor_name = data["doctor_name"]
    doctor_surname = data["doctor_surname"]
    doctor = doctor_name + " " + doctor_surname

    return render_template("found_patient.html", patient_name=name, patient_surname=surname, age=age, email=email, phone_num=phone_num, last_checkup_date=date, family_doctor=doctor, address=address)

@app.route("/create_report", methods=["GET", "POST"])
def create_report():
    if request.method == "POST":
        if request.form['add_new'] == "New":
            return redirect(url_for("new_report_type"))
        else:
            type = request.form['type']

            cursor = mysql.connection.cursor()
            sorgu = "Select * from diseases where diseases_name like '%" + type + "%'"
            result = cursor.execute(sorgu)

            if result == 0:
                flash("No report type suitable for the search term found", "yellow")
                return redirect(url_for("create_report"))
            else:
                types = cursor.fetchall()
                return render_template("create_report.html", types=types)
    else:
        return render_template("create_report.html")


@app.route("/report_create/<string:id>")
def report_create(id):
    session["diseases_id"] = id
    return redirect(url_for("selected_report_type"))

@app.route("/selected_report_type", methods=["GET", "POST"])
def selected_report_type():

    if request.method == "POST":
        details = request.form["details"]
        date_now = datetime.now()
        date_now = date_now.date()

        cursor = mysql.connection.cursor()
        query = "Insert into report(doctor_id, patient_id, diseases_id, starting_date, end_date, details) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (session["doctor_id"], session["found_patient"], session["diseases_id"], date_now, date_now, details))
        mysql.connection.commit()

        cursor = mysql.connection.cursor()
        query = "Select * From report where doctor_id = %s AND patient_id = %s AND diseases_id = %s AND starting_date = %s AND end_date = %s AND details = %s"
        result = cursor.execute(query, (session["doctor_id"], session["found_patient"], session["diseases_id"], date_now, date_now, details))
        data = cursor.fetchone()

        report_id = data["report_id"]
        comment = ""
        cursor = mysql.connection.cursor()
        query = "Insert into doctor_comments(report_id, doctor_id, patient_id, date, stars, comment) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (report_id, session["doctor_id"], session["found_patient"], date_now, 0, comment))
        mysql.connection.commit()


        return redirect(url_for("found_patient"))

    else:
        doctor_id = session["doctor_id"]
        cursor = mysql.connection.cursor()
        query = "Select * From doctors where doctor_id = %s"
        result = cursor.execute(query, (doctor_id,))
        data = cursor.fetchone()
        doctor_name = data["doctor_name"]
        doctor_surname = data["doctor_surname"]

        patient_id = session["found_patient"]
        cursor = mysql.connection.cursor()
        query = "Select * From patients where patient_id = %s"
        result = cursor.execute(query, (patient_id,))
        data = cursor.fetchone()
        patient_name = data["patient_name"]

        diseases_id = session["diseases_id"]
        cursor = mysql.connection.cursor()
        query = "Select * From diseases where diseases_id = %s"
        result = cursor.execute(query, (diseases_id,))
        data = cursor.fetchone()
        diseases_name = data["diseases_name"]

        return render_template("selected_report_type.html", doctor_name=doctor_name, doctor_surname=doctor_surname, patient_name=patient_name, report_type=diseases_name)


@app.route("/new_report_type", methods=["GET", "POST"])
def new_report_type():
    if request.method == "POST":
        name = request.form["name"]
        details = request.form["details"]

        cursor = mysql.connection.cursor()
        query = "Insert into diseases(diseases_name, details) VALUES(%s,%s)"
        cursor.execute(query, (name,details))
        mysql.connection.commit()

        flash("The new report type has been successfully created.","green")
        return redirect(url_for("create_report"))

    else:
        return render_template("new_report_type.html")

@app.route("/past_reports")
def past_reports():
    patient_id = session["found_patient"]

    cursor = mysql.connection.cursor()
    sorgu = "Select * From report where patient_id = %s"
    result = cursor.execute(sorgu, (patient_id,))

    if result > 0:
        details = cursor.fetchall()
        doctors = list()
        report_type = list()

        cursor = mysql.connection.cursor()
        sorgu = "Select * From patients where patient_id = %s"
        result = cursor.execute(sorgu, (patient_id,))
        patient = cursor.fetchone()
        patient_name = patient["patient_name"] + " " + patient["patient_surname"]


        for i in details:
            doctor_id = i["doctor_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From doctors where doctor_id = %s"
            result = cursor.execute(sorgu, (doctor_id,))
            doctor = cursor.fetchone()
            doctor_name = doctor["doctor_name"] + " " +doctor["doctor_surname"]
            doctors.append(doctor_name)

        for i in details:
            diseases_id = i["diseases_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From diseases where diseases_id = %s"
            result = cursor.execute(sorgu, (diseases_id,))
            diseases = cursor.fetchone()
            diseases_name = diseases["diseases_name"]
            report_type.append(diseases_name)

        doctors = tuple(doctors)
        report_type = tuple(report_type)
        return render_template("past_reports.html",list_length=len(details),patient_name=patient_name,doctors=doctors, diseases=report_type, reports=details)

    else:
        flash("There is no past report.", "red")
        return redirect(url_for("found_patient"))

@app.route("/create_prescription", methods=["GET", "POST"])
def create_prescription():
    if request.method == "POST":
        if request.form['add_new_drug'] == "New":
            return redirect(url_for("new_drug"))
        else:
            drug_name = request.form['drug_name']

            cursor = mysql.connection.cursor()
            sorgu = "Select * from drugs where drug_name like '%" + drug_name + "%'"
            result = cursor.execute(sorgu)

            if result == 0:
                flash("No drug suitable for the search term found", "yellow")
                return redirect(url_for("create_prescription"))
            else:
                drugs = cursor.fetchall()
                return render_template("create_prescription.html", drugs=drugs)
    else:
        return render_template("create_prescription.html")

@app.route("/new_drug", methods=["GET", "POST"])
def new_drug():
    if request.method == "POST":
        name = request.form["name"]
        details = request.form["details"]
        virtual = request.form["virtual"]

        if virtual == "yes":
            virtual = 1
        elif virtual == "no":
            virtual = 0

        cursor = mysql.connection.cursor()
        query = "Insert into drugs(drug_name, virtual_recipe, details) VALUES(%s,%s,%s)"
        cursor.execute(query, (name, virtual, details))
        mysql.connection.commit()

        flash("The new drug has been successfully created.", "green")
        return redirect(url_for("create_prescription"))

    else:
        return render_template("new_drug.html")

@app.route("/drug_create/<string:id>")
def drug_create(id):
    session["new_drug_id"] = id
    return redirect(url_for("create_new_prescription"))


@app.route("/create_new_prescription")
def create_new_prescription():
    date_now = datetime.now()
    date_now = date_now.date()
    is_virtual = 0

    cursor = mysql.connection.cursor()
    query = "Insert into prescription(doctor_id, patient_id, drug_id, date, is_virtual) VALUES(%s,%s,%s,%s,%s)"
    cursor.execute(query, (session["doctor_id"], session["found_patient"], session["new_drug_id"],date_now, is_virtual))
    mysql.connection.commit()
    flash("Prescription successfully added","green")
    return redirect(url_for("create_prescription"))


@app.route("/past_prescriptions")
def past_prescription():
    patient_id = session["found_patient"]

    cursor = mysql.connection.cursor()
    sorgu = "Select * From prescription where patient_id = %s"
    result = cursor.execute(sorgu, (patient_id,))

    if result > 0:
        details = cursor.fetchall()
        doctors = list()
        drug_names = list()
        virtuals = list()

        cursor = mysql.connection.cursor()
        sorgu = "Select * From patients where patient_id = %s"
        result = cursor.execute(sorgu, (patient_id,))
        patient = cursor.fetchone()
        patient_name = patient["patient_name"] + " " + patient["patient_surname"]


        for i in details:
            doctor_id = i["doctor_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From doctors where doctor_id = %s"
            result = cursor.execute(sorgu, (doctor_id,))
            doctor = cursor.fetchone()
            doctor_name = doctor["doctor_name"] + " " +doctor["doctor_surname"]
            doctors.append(doctor_name)

        for i in details:
            drug_id = i["drug_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From drugs where drug_id = %s"
            result = cursor.execute(sorgu, (drug_id,))
            drugs = cursor.fetchone()
            drug_name = drugs["drug_name"]
            drug_names.append(drug_name)

        for i in details:
            virtual = i["is_virtual"]

            if virtual == b'\x01':
                virtuals.append("Yes")
            elif virtual == b'\x00':
                virtuals.append("No")


        doctors = tuple(doctors)
        drug_names = tuple(drug_names)
        virtuals = tuple(virtuals)
        return render_template("past_prescription.html", list_length=len(details), patient_name=patient_name, doctors=doctors, drug_names=drug_names, prescription=details, is_virtual=virtuals)

    else:
        flash("There is no past prescription.", "red")
        return redirect(url_for("found_patient"))


@app.route("/doctor_search", methods=["GET", "POST"])
def doctor_search():
    if request.method == "POST":
        email = request.form['email']

        cursor = mysql.connection.cursor()
        sorgu = "Select * From doctors where e_mail = %s"
        result = cursor.execute(sorgu, (email,))

        if result == 0:
            flash("There is no doctor identified with this e-mail address.", "yellow")
            return redirect(url_for("doctor_search"))
        else:
            doctors = cursor.fetchone()
            return render_template("doctor_search.html", doctor=doctors)
    else:
        return render_template("doctor_search.html")


@app.route("/my_prescription")
def my_prescription():
    patient_id = session["patient_id"]

    cursor = mysql.connection.cursor()
    sorgu = "Select * From prescription where patient_id = %s"
    result = cursor.execute(sorgu, (patient_id,))

    if result > 0:
        details = cursor.fetchall()
        doctors = list()
        drug_names = list()
        virtuals = list()

        cursor = mysql.connection.cursor()
        sorgu = "Select * From patients where patient_id = %s"
        result = cursor.execute(sorgu, (patient_id,))
        patient = cursor.fetchone()
        patient_name = patient["patient_name"] + " " + patient["patient_surname"]


        for i in details:
            doctor_id = i["doctor_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From doctors where doctor_id = %s"
            result = cursor.execute(sorgu, (doctor_id,))
            doctor = cursor.fetchone()
            doctor_name = doctor["doctor_name"] + " " +doctor["doctor_surname"]
            doctors.append(doctor_name)

        for i in details:
            drug_id = i["drug_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From drugs where drug_id = %s"
            result = cursor.execute(sorgu, (drug_id,))
            drugs = cursor.fetchone()
            drug_name = drugs["drug_name"]
            drug_names.append(drug_name)

        for i in details:
            virtual = i["is_virtual"]

            if virtual == b'\x01':
                virtuals.append("Yes")
            elif virtual == b'\x00':
                virtuals.append("No")


        doctors = tuple(doctors)
        drug_names = tuple(drug_names)
        virtuals = tuple(virtuals)
        return render_template("my_prescription.html", list_length=len(details), patient_name=patient_name, doctors=doctors, drug_names=drug_names, prescription=details, is_virtual=virtuals)

    else:
        flash("There is no past prescription.", "red")
        return redirect(url_for("index"))


@app.route("/my_doctor")
def my_doctor():

    patient_id = session["patient_id"]
    cursor = mysql.connection.cursor()
    sorgu = "Select * From patients where patient_id = %s"
    result = cursor.execute(sorgu, (patient_id,))
    result = cursor.fetchone()
    doctor_id = result["family_doctor_id"]

    cursor = mysql.connection.cursor()
    sorgu = "Select * From doctors where doctor_id = %s"
    result = cursor.execute(sorgu, (doctor_id,))
    data = cursor.fetchone()

    name = data["doctor_name"]
    surname = data["doctor_surname"]
    age = data["age"]
    email = data["e_mail"]
    phone_num = data["phone_num"]
    profession = data["profession"]
    hospital = data["hospital"]

    return render_template("my_doctor.html", doctor_name=name, doctor_surname=surname, age=age, e_mail=email, phone_num=phone_num, profession=profession, hospital=hospital)

@app.route("/my_comments")
def my_comments():
    patient_id = session["patient_id"]


    cursor = mysql.connection.cursor()
    sorgu = "Select * From doctor_comments where patient_id = %s"
    result = cursor.execute(sorgu, (patient_id,))

    if result > 0:
        comments = cursor.fetchall()
        doctors = list()

        for i in comments:
            doctor_id = i["doctor_id"]
            cursor = mysql.connection.cursor()
            sorgu = "Select * From doctors where doctor_id = %s"
            result = cursor.execute(sorgu, (doctor_id,))
            doctor = cursor.fetchone()
            doctor_name = doctor["doctor_name"] + " " + doctor["doctor_surname"]
            doctors.append(doctor_name)

        doctors = tuple(doctors)

        return render_template("my_comments.html", list_length=len(comments), doctors=doctors, comments=comments)

    else:
        flash("There is no past comment.", "red")
        return redirect(url_for("index"))

@app.route("/comment_change/<string:id>")
def comment_change(id):
    session["change_comment_id"] = id
    return redirect(url_for("update_comments"))

@app.route("/update_comments", methods=["GET", "POST"])
def update_comments():
    if request.method == "POST":
        stars = request.form["stars"]
        comment = request.form["comment"]

        stars = int(stars)


        cursor = mysql.connection.cursor()
        query = "Update doctor_comments Set stars = %s,comment = %s where report_id = %s"
        result = cursor.execute(query, (stars, comment, session["change_comment_id"]))
        mysql.connection.commit()

        flash("The doctor comment has been updated successfully.","green")
        return redirect(url_for("my_comments"))


    else:
        cursor = mysql.connection.cursor()
        query = "Select * From doctor_comments where report_id = %s"
        result = cursor.execute(query, (session["change_comment_id"],))
        data = cursor.fetchone()
        return render_template("update_comments.html",comment=data["comment"])


if __name__ == "__main__":
    app.run(debug=True)
