import requests, string, random, json
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from dotenv import load_dotenv
import smtplib

load_dotenv()
url = "https://api.segmind.com/v1/kandinsky2.1-txt2img"
api_key = os.getenv("API_KEY")
my_email = os.getenv("MY_EMAIL")
email_password = os.getenv("MY_PASSWORD")
f = open('data.json')
data = json.load(f)
era_dict = {'Ancient':"Ancient era", 'Victor':"Victorian era",'modern':"Modern era", 'Post-clas':"Post-Classical Era"}

def get_image(prompt):
    data = {
    "prompt": prompt,
    "negative_prompt": "NONE",
    "samples": "1",
    "scheduler": "DDIM",
    "num_inference_steps": "40",
    "guidance_scale": "9",
    "seed": "1006",
    "img_width":"512",
    "img_height":"512"
    }

    response = requests.post(url, json=data, headers={"x-api-key": f"{api_key}"})
    image = Image.open(BytesIO(response.content))
    return image

def generate_random_password(length):
    characters = string.ascii_letters + string.digits + "!#$%&*+?@^"*2
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL",  "sqlite:///blog.db")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == 'POST':
        flash("Thanks for approaching us, we'll get back to you soon!")
        return render_template("index.html")
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['pass']
        email = request.form['email-change']
        user = User.query.filter_by(name=name).first()
        
        if 'change' in request.form:
            if email:
                user = User.query.filter_by(email=email).first()
                if not user:
                    flash ("This email does not exist, please register.")
                    return redirect(url_for('register'))
                password = generate_random_password(10)
                password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                user.password = password_hash
                db.session.commit()
                connection = smtplib.SMTP("smtp.gmail.com", 587)
                connection.starttls()
                connection.login(user=my_email, password=email_password)
                connection.sendmail(from_addr=my_email, to_addrs=email,
                                    msg=f"Subject: Password change - Timeless Mueseum\n\n Your password has been changed to {password}")
                connection.close()
                flash("Your password has been changed, please check your email. Login with your new password.")
                return redirect(url_for('login'))
        elif 'login' in request.form:
            if not user:
                flash("This user does not exist, please register.")
                return redirect(url_for('register'))
            elif not check_password_hash(user.password, password):
                flash("Password incorrect, please try again.")
                return redirect(url_for('login'))
            else:
                login_user(user)
                return redirect(url_for('homepage'))
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        if pass1 != pass2:
            flash("Passwords don't match")
            return redirect(url_for('register'))
        if User.query.filter_by(name=name).first():
            flash("That name already exists, please try another name.")
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            hashed_pass = generate_password_hash(pass1, method='pbkdf2:sha256', salt_length=8)
            new_user = User(name=name, email=email, password=hashed_pass)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('homepage'))
    return render_template("signup.html")

@app.route('/homepage', methods = ['GET','POST'])
def homepage():
    if request.method == 'POST':
        country = request.form['country_name']
        era = request.form['era']
        return redirect(url_for('images', country=country, era=era, page=0))
    return render_template('map.html', name=current_user.name)

@app.route('/images/<country>/<era>/<int:page>', methods = ['GET','POST'])
def images(country, era, page):
    if country not in data:
        print(country)
        flash('This country is not yet supported, please try again.')
        return redirect(url_for('homepage'))
    painting = data[country][page]['painting']
    artist = data[country][page]['artist']
    prompt = painting + " by " + artist + " in the " + era_dict[era] + " era"
    if os.path.exists(f'static/images/{country}_{era}_{page}.jpg'):
        return render_template('image.html',path=f'images/{country}_{era}_{page}.jpg', painting=painting, artist=artist, country=country, era=era, page=page, era_name = era_dict[era])
    else:
        image = get_image(prompt)
        image.save(f'static/Images/{country}_{era}_{page}.jpg')
        return render_template('image.html',path=f'images/{country}_{era}_{page}.jpg', painting=painting, artist=artist, country=country, era=era, page=page, era_name = era_dict[era])
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run(debug=True)