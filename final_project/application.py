import os
import re

from cs50 import SQL
from decimal import getcontext, Decimal
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///school.db")

@app.route("/")
@login_required
def index():
        rows = db.execute("SELECT SUM(student_total) AS stdtotal, SUM(payment_total) AS paytotal, COUNT(identifier) AS clstotal FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        # If no class has been added yet, set student total and paytotal to zero
        if (rows[0]["clstotal"] == 0):
            rows[0]["stdtotal"] = 0
            rows[0]["paytotal"] = 0
        return render_template("index.html", data=rows[0])


@app.route("/register", methods=["GET", "POST"])
def register():
        """Admin Registration"""
        if request.method == "POST":
            password = request.form.get("password")
            user = request.form.get("username")

            # Hash the password for extra security
            hashed = generate_password_hash(password)

            # Check for username
            result = db.execute("INSERT INTO admins (name, pword) VALUES (:name,:pword)",
                                name=user, pword=hashed)

            # Check whether username is already taken
            if not result:
                flash("Username already taken", "error")
                return redirect("/register")

            # Store user's session ID
            rows = db.execute("SELECT * FROM admins WHERE name = :username", username=user)
            session["user_id"] = rows[0]["id"]

            flash("Registration Successful", "success")
            return redirect("/")
        else:
            return render_template("adm_register.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Admin Account"""
    if request.method == "POST":
        userid = session["user_id"]
        newname = request.form.get("username")
        newpword = request.form.get("password")
        cur_pword = request.form.get("cur_pword")

        rows = db.execute("SELECT * FROM admins WHERE id=:userid", userid=userid)
        if len(rows) != 1 or not check_password_hash(rows[0]["pword"], cur_pword):
            flash("Current password is wrong!", "error")
            return redirect("/account")
        else:
            # Both username and password entered
            if (newname != "") and (newpword != ""):
                # Check for duplicates for username chosen
                namechk = db.execute("SELECT * FROM admins WHERE name = :name", name=newname)
                if namechk:
                    flash("Username already taken", "error")
                    return redirect("/account")
                else:
                    hashed = generate_password_hash(newpword)
                    db.execute("UPDATE admins SET name = :value1, pword = :value2 WHERE id = :userid",
                               value1=newname, value2=hashed, userid=userid)
                    flash("Your information has been successfully updated", "success")
                    return redirect("/account")

            # Only username entered
            # Cannot check for none
            elif newname != "":
                # Check whether the username is already taken
                namechk = db.execute("SELECT * FROM admins WHERE name = :name", name=newname)
                if namechk:
                    flash("Username already taken", "error")
                    return redirect("/account")
                else:
                    db.execute("UPDATE admins SET name = :value WHERE id = :userid", value=newname, userid=userid)
                    flash("Username updated successfully", "success")
                    return redirect("/account")

            # Only password entered
            elif newpword != "":
                # If the new password is not the same as the confirmation password
                hashed = generate_password_hash(newpword)
                db.execute("UPDATE admins SET pword = :value WHERE id = :userid", value=hashed, userid=userid)
                flash("Password updated successfully", "success")
                return redirect("/account")
    else:
        rows = db.execute("SELECT * FROM admins WHERE id=:userid", userid=session["user_id"])
        return render_template("profile.html", admin=rows[0])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.clear()

        rows = db.execute("SELECT * FROM admins WHERE name = :admin",
                          admin=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pword"], request.form.get("password")):
            flash("Username/Password Incorrect!", "error")
            return redirect("/login")
        else:
            session["user_id"] = rows[0]["id"]
            return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_class", methods=["GET", "POST"])
@login_required
def add_class():
    if request.method == "POST":
        level = request.form.get("className")
        date = request.form.get("date")
        period = request.form.get("period")
        teacher=request.form.get("teacher")

        # Changing the time format of 24 hrs to 12 hrs
        period = period.replace(":", ".")
        period = float(period)

        period = Decimal(period)
        if period < 6 or period > 23:
            flash("The time is not allowed", "error")
            return redirect("/add_class")

        if period >= 13:
            period = period - Decimal(12.00)
            timeOfDay = "PM"
        else:
            timeOfDay = "AM"
        period = round(period, 2)
        period = str(period)
        period = period.replace(".", ":")

        # Change the date format from yy-mm-dd to dd-mm-yy
        temp = date.split("-")
        date = temp[2] + "-" + temp[1] + "-" + temp[0]

        class_id = level + " " + date + " (" + period + ") " + timeOfDay + " by " + teacher

        # Check whether the class exists or not
        class_check = db.execute("SELECT * FROM classes WHERE identifier = :id AND admin_id = :admID", id=class_id, admID=session["user_id"] )
        if not class_check:
            db.execute("""INSERT INTO classes (admin_id, classname, teacher, fee, classDate, period_start, identifier)
                       VALUES(:admID, :level, :teacher, :fee, :startingDate, :period, :identifier)""",
                       admID=session["user_id"], level=level, teacher=teacher,
                       fee=request.form.get("fees"), startingDate=date,
                       period=period + " " + timeOfDay, identifier=class_id)
            return redirect("/add_class")
        else:
            flash("Class already exists", "error")
            return redirect("/add_class")

    else:
        class_check = db.execute("SELECT * FROM classes WHERE admin_id = :admID",
                                  admID=session["user_id"])
        return render_template("addClass.html", classes=class_check)


@app.route("/manage_class", methods=["GET", "POST"])
@login_required
def manage_class():
    if request.method == "POST":
        class_id = request.form.get("class_id")
        db.execute("DELETE FROM students WHERE class_id = :id AND admin_id = :admID", id=class_id, admID=session["user_id"])
        db.execute("DELETE FROM classes WHERE identifier = :id AND admin_id = :admID", id=class_id, admID=session["user_id"])
        db.execute("DELETE FROM payment WHERE class_id = :id AND admin_id = :admID", id=class_id, admID=session["user_id"])

        return redirect("/manage_class")
    else:
        rows = db.execute("SELECT * FROM classes WHERE admin_id = :admID", admID=session["user_id"])

        # Get the number of classes registered in the database
        numClass = db.execute("SELECT COUNT(identifier) AS numOfClass FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        return render_template("mngclasses.html",numClass=numClass[0]["numOfClass"], classes=rows)


@app.route("/register_student", methods=["GET", "POST"])
@login_required
def register_student():
    if request.method == "POST":
        # index for while loop
        i = 0

        student_exist = ""
        program = request.form.get("program")
        name = request.form.get("studentName")
        nickname = request.form.get("nickname")
        numOfStudents = request.form.get("studentNumber")
        name = name.lower()
        nickname = nickname.lower()

        if nickname != "":
            nickname = nickname.lower()
            student_exist = db.execute("SELECT * FROM students WHERE class_id = :level and name = :name and nickname = :nick and admin_id = :admID",
                        level=program, name=name, nick=nickname, admID=session["user_id"])
        else:
            student_exist = db.execute("SELECT * FROM students WHERE class_id = :level and name = :name and admin_id = :admID",
                        level=program, name=name, admID=session["user_id"])
        if not student_exist:
            db.execute("""INSERT INTO students (name, nickname, class_id, student_id, admin_id)
                       VALUES (:name, :nick, :level, :std_id, :admID)""", name=name, nick=nickname,
                       level=program, std_id=name+nickname, admID=session["user_id"])
            flash(u"{} added successfully".format(name + " " + nickname), "success")
        else:
            flash(u"{} is already registered in the class".format(name + " " + nickname), "error")

        # Handles multiple student registration
        if numOfStudents != "":
            numOfStudents = int(numOfStudents)
            while (numOfStudents != 0):
                temp_exist = ""
                temp_name = request.form.get("studentName" + str(i))
                temp_nick = request.form.get("nickname" + str(i))
                temp_name = temp_name.lower()
                temp_nick = temp_nick.lower()
                if temp_nick != "":
                    temp_exist = db.execute("SELECT * FROM students WHERE class_id = :level AND name = :name and nickname = :nick and admin_id=:admID",
                                               level=program, name=temp_name, nick=temp_nick, admID=session["user_id"])
                else:
                    temp_exist = db.execute("SELECT * FROM students WHERE class_id = :level AND name = :name AND admin_id = :admID",
                                            level=program, name=temp_name, admID=session["user_id"])
                if temp_exist:
                    flash("{} is already registered in the class.".format(temp_name + " " + temp_nick), 'error')
                else:
                    db.execute("""INSERT INTO students (admin_id, name, nickname, class_id, student_id)
                               VALUES (:admID, :name, :nick, :level, :std_id)""", name=temp_name,
                               nick=temp_nick, level=program, std_id=temp_name+temp_nick, admID=session["user_id"])
                    flash(u"{} added successfully".format(temp_name + " " + temp_nick), "success")
                i += 1
                numOfStudents -= 1
        # Count for the total number of students in the class and updates it for the respective class
        numStudents = db.execute("SELECT COUNT(student_id) AS numOfstudents FROM students WHERE class_id = :identifier AND admin_id = :admID",
                                 identifier=program, admID=session["user_id"])
        db.execute("UPDATE classes SET student_total = :total WHERE identifier = :identifier AND admin_id = :admID",
                   total=numStudents[0]["numOfstudents"], identifier=program, admID=session["user_id"])

        # Update total fees per class
        classinfo = db.execute("SELECT * FROM classes WHERE identifier = :id AND admin_id = :admID", id=program, admID=session["user_id"])
        stdnum = classinfo[0]["student_total"]
        fees = classinfo[0]["fee"]
        totalpay = stdnum * fees
        db.execute("UPDATE classes SET payment_total = :total WHERE identifier = :id AND admin_id = :admID", total=totalpay, id=program, admID=session["user_id"])

        return redirect("/register_student")
    else:
        rows = db.execute("SELECT identifier FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        # Get the number of classes registered in the database to display none if there is no class
        counter = db.execute("SELECT COUNT(identifier) AS numOfClass FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        return render_template("studentReg.html",numClass=counter[0]["numOfClass"], classes=rows)

@app.route("/manage_student", methods=["POST", "GET"])
@login_required
def manage_student():
    if request.method == "POST":
        program = request.form.get("program")
        students = request.form.getlist("student")
        temp = []

        # Here is where the plus signs are broken apart from the 'students' list
        str_break_up = [i.split('+') for i in students]

        for i in str_break_up:
            db.execute("DELETE FROM students WHERE class_id = :id AND name = :name AND nickname = :nick AND admin_id = :admID",
                       id=program, name=i[0], nick=i[1], admID=session["user_id"])
            db.execute("DELETE FROM payment WHERE class_id = :id AND name = :name AND nickname = :nick AND admin_id = :admID",
                           id=program, name=i[0], nick=i[1], admID=session["user_id"])

        # Count for the total number of students in the class and updates it for the respective class
        numStudents = db.execute("SELECT COUNT(name) AS numOfstudents FROM students WHERE class_id = :identifier AND admin_id = :admID",
                                 identifier=program, admID=session["user_id"])
        db.execute("UPDATE classes SET student_total = :total WHERE identifier = :identifier AND admin_id = :admID",
                   total=numStudents[0]["numOfstudents"], identifier=program, admID=session["user_id"])
        # Return the class that was selected by the user along with deleting the duplicate of it from the dropdown list
        rows = db.execute("SELECT identifier FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        for i in rows:
            if i["identifier"] == program:
                del i["identifier"]
        while {} in rows:
            rows.remove({})
        return render_template("studentmng.html", classesXceptone=rows, selected=1, Xcepted_one=program)

    else:
        rows = db.execute("SELECT identifier FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        return render_template("studentmng.html", classes=rows, selected=0)


@app.route("/getstudents")
def getstudents():
    program = request.args.get("program")
    students = db.execute("SELECT * FROM students WHERE class_id = :id AND admin_id = :admID",
                           id=program, admID=session["user_id"])

    return jsonify(students)


@app.route("/getclasses")
def getclasses():
    program = request.args.get("program")
    classes = db.execute("SELECT classDate FROM classes WHERE identifier = :id AND admin_id = :admID",
                         id=program, admID=session["user_id"])

    return jsonify(classes)


@app.route("/getpayment")
def getpayment():
    program = request.args.get("program")
    payment = db.execute("SELECT * FROM payment WHERE class_id = :id AND admin_id = :admID",
                         id=program, admID=session["user_id"])

    return jsonify(payment)


@app.route("/getStats")
def getStats():
    classNames = request.args.get("classes")
    classNames = classNames.replace("[", "")
    classNames = classNames.replace("]", "")
    classNames = classNames.replace('"', "")
    classNames = classNames.split(",")
    numofclasses = []

    for i in classNames:
        temp = i + "%"
        numofclasses += db.execute("SELECT COUNT(identifier) AS :type FROM classes WHERE identifier LIKE :id AND admin_id = :admID",
                          type=i, id=temp, admID=session["user_id"])
    return jsonify(numofclasses)


@app.route("/manage_payment", methods=["POST", "GET"])
@login_required
def manage_payment():
    if request.method == "POST":
        program = request.form.get("program")
        students = request.form.getlist("student")
        # variable for unchecked checkboxes for already paid ones
        unchecked = request.form.getlist("unchecks")
        print(unchecked)
        temp = []
        nametmp = []
        paytmp = []
        name = []
        payrec = []
        pay_month = []
        pay_yr = []

        # Push it into the students variable if unchecked is not empty as the value is just the same as the students variable, only changing the paid status back
        if len(unchecked) != 0:
            students = unchecked

        # Here is where the name and payment time are broken apart from the 'students' list
        str_break_up = [i.split(',') for i in students]
        print(str_break_up)

        for i in str_break_up:
            temp.append(list(filter(None, i)))

        # Here is where the strings from the broken lists are separated into name and payrec variables
        for i in temp:
            name.append(i[0])
            payrec.append(i[1])

        name = [i.split('+') for i in name]
        payrec = [i.split('+') for i in payrec]

        for i in payrec:
            paytmp.append(list(filter(None, i)))

        for i in paytmp:
            pay_month.append(i[0])
            pay_yr.append(i[1])

        if len(unchecked) == 0:
            index = 0
            for j in name:
                # Select from payment table first to update the student paycheck
                student_check = db.execute("SELECT * FROM payment WHERE name = :name AND nickname = :nick AND class_id = :id AND Paidyear = :year AND admin_id = :admID",
                                           name=j[0], nick=j[1], id=program, year=pay_yr[index], admID=session["user_id"])
                if not student_check:
                    db.execute("INSERT INTO payment (admin_id, name, nickname, class_id, :month, Paidyear) VALUES (:admID, :name, :nick, :id, 'PAID', :year)",
                                name=j[0], nick=j[1], month="{}".format(pay_month[index]), id=program, year=pay_yr[index], admID=session["user_id"])
                else:
                    db.execute("UPDATE payment SET :month = 'PAID' WHERE name = :name AND nickname = :nick AND class_id = :id AND Paidyear = :year AND admin_id = :admID",
                               month="{}".format(pay_month[index]), name=j[0], nick=j[1], id=program, year=pay_yr[index], admID=session["user_id"])

                index += 1
        else:
            # Change the paid status of students back again
            index = 0;
            for j in name:
                db.execute("UPDATE payment SET :month = 'UNPAID' WHERE name = :name AND nickname = :nick AND class_id = :id AND Paidyear = :year AND admin_id = :admID",
                           month="{}".format(pay_month[index]), name=j[0], nick=j[1], id=program, year=pay_yr[index], admID=session["user_id"])
                index += 1

        # Delete the duplicated class name from the dropdown list in the select box
        rows = db.execute("SELECT identifier FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        for i in rows:
            if i["identifier"] == program:
                del i["identifier"]
        while {} in rows:
            rows.remove({})
        return render_template("payment.html", classesXceptone=rows, selected=1, Xcepted_one=program)
    else:
        rows = db.execute("SELECT identifier FROM classes WHERE admin_id = :admID", admID=session["user_id"])
        return render_template("payment.html", classes=rows, selected=0);


# CS50 similarities error handler
@app.errorhandler(HTTPException)
def errorhandler(error):
    """Handle errors"""
    return render_template("error.html", error=error), error.code


# https://github.com/pallets/flask/pull/2314
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run()
