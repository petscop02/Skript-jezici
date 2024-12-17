from flask import redirect, session
from functools import wraps
from random import randint
import yagmail
import os
import fpdf
import PyPDF2

def check_password_characters(psw):
    count1 = 0
    count2 = 0
    count3 = 0
    count4 = 0
    lower = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    upper = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    numb = ['0','1','2','3','4','5','6','7','8','9']
    for i in psw:
        if i in lower:
            count1 += 1
        elif i in upper:
            count2 += 1
        elif i in numb:
            count3 += 1
        else:
            count4 += 1
    if count1 == 0 or count2 == 0 or count3 == 0 or count4 == 0:
        return True
    

def login_required(f):
    #https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None: #ukoliko korisnik nije prijavljen, posalji ga da se prijavi
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def send_mail(email):
    message = yagmail.SMTP('dimitrijegajic55@gmail.com')
    code = randint(1000,1000000)
    check = str(code)
    message.send(email,'Code',str(code))
    return check
    
yagmail.register('email','password') # placeholder

class PDF:
    def __init__(self,title,choice):
        self.title = title
        self.choice = choice
    
    def write(self,title,choice,image):
        self = fpdf.FPDF('L')
        self.add_page()
        self.set_font('Times','B',16)
        self.cell(0,0,"Statistics",0,0,'C')
        self.set_font('Times','',16)
        self.write(10,f"Hello {title}! Your chosen object was {choice}! Why though? Why did you choose {choice}?\n") 
        self.write(15,f"I hope that you do not regret yout desicion...")
        self.cell(1,80)
        self.image(image,w=200,h=150)
        self.output("static/a.pdf")
