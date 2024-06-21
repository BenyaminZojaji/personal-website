import os
import time
from flask import Flask, send_file, render_template, request, redirect, url_for, session
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel
from enc import Encryption

app = Flask(__name__)


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    username: str = Field()
    age: int = Field()
    city: str = Field()
    country: str = Field()
    password: str = Field()
    join_time: str = Field()
    
engine = create_engine('sqlite:///./database.db', echo=True)
SQLModel.metadata.create_all(engine)

class RegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    age: int
    city: str
    country: str
    password: str
    confirm_password: str
    join_time: int
    
    
class LoginModel(BaseModel):
    username: str
    password: str

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/login", methods=['GET', "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    
    elif request.method == "POST":
        try:
            login_model = LoginModel(
                username = request.form["username"],
                password = request.form["password"])
            
        except:
            print('Type Error')
            return redirect(url_for('login'))
        
        with Session(engine) as db_session:
            statement = select(User).where(User.username == login_model.username)
            result = db_session.exec(statement).first()
        
        if result:
            enc_obj = Encryption()
            if enc_obj.check(login_model.password, result.password):
                print('welcome, you are logged in')
                return redirect(url_for('home'))
            else:
                print('Password is incorrect')
                return redirect(url_for('login'))
        else:
            print('Username is incorrect')
            return redirect(url_for('login'))


@app.route("/register", methods=['GET', "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    
    elif request.method == "POST":
        try:
            register_data = RegisterModel(
                first_name=request.form["first_name"],
                last_name=request.form["last_name"],
                email=request.form["email"],
                username=request.form["username"],
                age=request.form["age"],
                city=request.form["city"], 
                country=request.form["country"],
                password=request.form["password"],
                confirm_password=request.form["confirm_password"],
                join_time=int(time.time())
                )
        except Exception as e:
            print('Type Error')
            print (e)
            return redirect(url_for('register'))
            
            
        with Session(engine) as db_session:
            statement = select(User).where(User.username == register_data.username)
            result = db_session.exec(statement).first()
            
        if not result:
            if register_data.confirm_password == register_data.password:
                enc_obj = Encryption()
                hashed_password = enc_obj.hash_password(register_data.password)
                with Session(engine) as db_session:
                    user = User(
                        first_name=register_data.first_name,
                        last_name=register_data.last_name,
                        email=register_data.email,
                        username=register_data.username,
                        age=register_data.age,
                        city=register_data.city,
                        country=register_data.country,
                        password=hashed_password,
                        join_time=register_data.join_time
                        )
                    db_session.add(user)
                    db_session.commit()
                    print('Your register done succesfully.')
                    return redirect(url_for('login'))
            else:
                print('Passwords are not match.')
                return redirect(url_for('register'))  
        else:
            print('username already exist, Try another username.')
            return redirect(url_for('register'))


@app.route("/blog")
def blog():
    return render_template('blog.html')


@app.route('/resume_download')
def resume_download():
    path = os.path.join('pdf', 'BenyaminZojaji-resume2024.pdf')
    return send_file(path)


if __name__ == '__main__':
    app.run(debug=True)
