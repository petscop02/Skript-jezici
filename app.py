from flask import *
from flask_session import *
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from other_functions import check_password_characters, login_required, send_mail, PDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


db = SQL("sqlite:///database.db")

app = Flask(__name__) # kreiranje objekta app
app.config["SESSION_TYPE"] = "filesystem" # cuvamo sesije u fajlu a ne u preko cookies-a
Session(app) 
global check,check_email

@app.after_request #ukoliko se korisnik prijavi a potom ode nazad, morace opet da unese podatke, tjt nemoj pamitit podatke
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response 


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/delete",methods=["GET","POST"])
@login_required
def delete():
    if request.method == "GET":
        return render_template("delete.html")
    else:
        username = request.form.get("username")
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if username != session["user_name"]:
            return render_template("delete.html",error_message="You can't delete someone's else account!")
        else:
            psw = db.execute("SELECT password FROM users WHERE username = ?",username)
            password_db = psw[0].get('password')
            if not(check_password_hash(password_db,password)):
                return render_template("delete.html",error_message="Invalid password!")
            if password2 != password:
                return render_template("delete.html",error_message="Please confirm your password")
            db.execute("DELETE FROM users WHERE username = ?",username)
            db.execute("DELETE FROM history WHERE username = ?", username)
            all_history = db.execute("SELECT * FROM history")

            j = 0
            for i in all_history:
                j += 1
                db.execute("UPDATE history SET id=? WHERE username=?",j,i.get('username'))

            session.clear()
            return redirect("/")
        


@app.route("/login",methods=["GET","POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html",error_message="")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "" or password == "": # setio sam se da postoji required u html ali nema veze ovako bih radio da ne postoji
            return render_template("login.html",error_message="Incorrect Input!")
        
        count = 0 # count za korisnike
        all_db = db.execute("SELECT * FROM users")

        for i in all_db: # prodji kroz korisnike i vidi da li postoje
            real_username = i.get('username')
            if username == real_username:
                count += 1

        if count == 0:
            return render_template("login.html", error_message="There is no such user!")
        
        psw = db.execute("SELECT password FROM users WHERE username = ?", username) # vadnjenje odgovarajuce lozinke
        password_db = psw[0].get('password')
        if not check_password_hash(password_db,password): # provera lozinke
            return render_template("login.html",error_message = "Invalid password!")
        
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?",username) # zapamti korisnika'''
        session["user_name"] = username
        return redirect("/")


@app.route("/forgot",methods=["GET","POST"])
def forgot():
    global check,check_email
    if request.method == "GET":
        return render_template("forgot.html")
    else:
        email = request.form.get('email')
        email_db = db.execute("SELECT * FROM users")
        count = 0
        for i in email_db:
            if email == i.get('email'):
                count += 1
        if count == 0:
            return render_template("forgot.html",error_message="There is no such e-mail!")
        check = send_mail(email) # provera da vidimo da li je kod dobar
        check_email = email # skladistenje emaila da znamo kom korisniku password da promenimo
        #print("FORGOT: ",check_email)
        #print("FORGOT: ",check)
        return redirect("/reset")
        

@app.route("/reset",methods=["GET","POST"])
def reset():
    global check
    #print("RESET: ",check)
    if request.method == "GET":
        return render_template("reset.html")
    else:
        code = request.form.get('code')
        if code != check:
            return render_template("reset.html",error_message="Your code is not correct!")
        return redirect("/new")


@app.route("/new",methods=["GET","POST"])
def new():
    global check_email
    #print("NEW: ",check_email)
    if request.method == "GET":
        return render_template("new.html")
    else:
        new = request.form.get('new')
        new2 = request.form.get('new2')
        if (len(new) > 0 and (len(new) < 8 or len(new)>24)): #duzina lozinke
            return render_template("new.html",error_message = "Password must be between 8 and 24 characters!")
            
        if (check_password_characters(new)) == True: #proveravamo da li je loznka zadovoljila uslove za karaktere
            return render_template("new.html",error_message = "Password must contain at least one of these: A,a,1,!")
            
        if new2 != new:
            return render_template("new.html",error_message = "Please confirm your password!")
        new_hash = generate_password_hash(new)
        db.execute("UPDATE users SET password = ? WHERE email=?",new_hash,check_email)
        return redirect("/login")


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html",error_message="")
    else:
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if email == '' or username == '' or password == '' or password2 == '': #ukoliko je korisnik uneo nesto, proveravamo sve redom (odgovarajuca duzina lozinki, da li su iste lozinke, da li korisnik vec postoji)
            return render_template("register.html",error_message = "Incorrect input!")
        else:
            email_db = db.execute("SELECT email FROM users") # izaberi sve e-mailove iz baze
            username_db = db.execute("SELECT username FROM users") # izaberi sve korisnike iz baze

            for i in email_db: # prodji kroz sve mejlove
                if email == i.get('email'): # email_db vraca listu recnika
                    return render_template("register.html",error_message = "There's alrady account with that email address!")
                
            for i in username_db: # prodji kroz sve usere (prolazi kroz recnike)
                if username == i.get('username'): # provera da li je korisnicko ime vec zauzeto
                    return render_template("register.html",error_message = "That username is already taken!")
                
            # ukoliko nije pronasao ni usera ni email, proverava lozinke i posle toga registruje

            if (len(password) > 0 and (len(password) < 8 or len(password)>24)): #duzina lozinke
                return render_template("register.html",error_message = "Password must be between 8 and 24 characters!")
            
            if (check_password_characters(password)) == True: #proveravamo da li je loznka zadovoljila uslove za karaktere
                return render_template("register.html",error_message = "Password must contain at least one of these: A,a,1,!")
            
            if password2 != password:
                 return render_template("register.html",error_message = "Please confirm your password!")
            # ukoliko je sve ovo proslo, sacuvamo podatke u bazi podataka

            hash_password = generate_password_hash(password) # lozinka se hashuje radi bezbednosti
            db.execute("INSERT INTO users(email,username,password,choice) VALUES (?,?,?,?)",email,username,hash_password,"not chosen yet")
            db.execute("INSERT INTO history(username,past) VALUES(?,?)",username,0)
            all_history = db.execute("SELECT * FROM history")
            j = 0
            for i in all_history:
                j += 1
                db.execute("UPDATE history SET id=? WHERE username=?",j,i.get('username'))
            # nakon unosa posalji korisnika na login stranicu

            return redirect("/login")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/choose", methods=["GET","POST"])
@login_required
def choose():
    if request.method == "GET":
        return render_template("choose.html",history=db.execute("SELECT * FROM history"))
    else:
        list1 = []
        dict1 = {}
        dict2 = {}
        choice = request.form.get("choice")
        check = request.form.get('check')
        why = request.form.get('why')
        new_past = 0

        pom = session["user_id"] #posto je session["user_id"] lista u kom se nalazi recnik
        usr_id = pom[0].get('id')
        history_db = db.execute("SELECT * FROM history")

        for i in history_db:
            if session["user_name"] == i.get('username'):
                new_past = i.get('past')
        new_past += 1

        db.execute("UPDATE users SET choice = ? WHERE id = ?",choice.lower(),usr_id) #updatovanje objekta posto je default "not chosen yet"
        db.execute("UPDATE history SET past = ? WHERE username = ?",new_past,session["user_name"])
        all_choice = db.execute("SELECT choice FROM users")

        for i in all_choice: # uzmi sve izbore
            list1.append(i.get('choice'))

        for i in list1: # prebroji ih
            if i in dict1:
                dict1[i] += 1
            else:
                dict1[i] = 1

        for key,value in dict1.items(): #izracunaj procenat izbora i skladisti u novi recnik
            key1 = key
            percentage = (float(value)/float(len(dict1))) * 100 #dobijanje procenta
            dict2[key1] = percentage
        
        try:
            os.remove("static/graph.png")
        except OSError:
            pass

        labels = list(dict2.keys()) #izdvoji kljuceve i vrednosti da mozemo da pravimo grafik
        sizes = list(dict2.values())

        plt.pie(sizes,labels=labels,autopct='% 1.1f%%')
        plt.savefig("static/graph.png")
        plt.close()

        pdf = PDF(session["user_name"],choice)
        pdf.write(pdf.title,pdf.choice,why,"static/graph.png")
        
        if check == None:
            pass
        else:
            render_template("choose.html",history = db.execute("SELECT * FROM history"))
            download_file = "static/a.pdf"
            return send_file(download_file,as_attachment=True)
        render_template("choose.html",history = db.execute("SELECT * FROM history"))
        return redirect(url_for("choose"))


app.run()
