import os
import time
from flask import Flask, flash, send_file, render_template, request, redirect, url_for, session as flask_session
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel
from enc import Encryption


app = Flask(__name__)
APP_SECRET_KEY = os.environ['APP_SECRET_KEY']
app.secret_key = APP_SECRET_KEY


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
            flash('Type Error', 'danger')
            return redirect(url_for('login'))
        
        with Session(engine) as db_session:
            statement = select(User).where(User.username == login_model.username)
            user = db_session.exec(statement).first()
        
        if user:
            enc_obj = Encryption()
            if enc_obj.check(login_model.password, user.password):
                flash('welcome, you are logged in', 'success')
                flask_session["user_id"] = user.id
                return redirect(url_for('home'))
            else:
                flash('Password is incorrect', 'warning')
                return redirect(url_for('login'))
        else:
            flash('Username is incorrect', 'warning')
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
        except:
            flash('Type Error', 'danger')
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
                    flash('Your register done successfully.', 'success')
                    return redirect(url_for('login'))
            else:
                flash('Passwords are not match.', 'warning')
                return redirect(url_for('register'))  
        else:
            flash('username already exist, Try another username.', 'warning')
            return redirect(url_for('register'))


@app.route("/logout")
def logout():
    flask_session.pop("user_id")
    return redirect(url_for("index"))


@app.route("/blog")
def blog():
    return render_template('blog.html')


@app.route('/resume_download')
def resume_download():
    path = os.path.join('pdf', 'BenyaminZojaji-resume2024.pdf')
    return send_file(path)


if __name__ == '__main__':
    app.run(debug=True)
