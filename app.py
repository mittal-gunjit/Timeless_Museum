import requests
from PIL import Image
from io import BytesIO
from flask import Flask, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from dotenv import load_dotenv

load_dotenv()
url = "https://api.segmind.com/v1/kandinsky2.1-txt2img"
api_key = os.getenv("API_KEY")

def get_image(prompt):
    data = {
    "prompt": prompt,
    "negative_prompt": "NONE",
    "samples": "1",
    "scheduler": "PLMS",
    "num_inference_steps": "20",
    "guidance_scale": "7.5",
    "seed": "1024",
    "img_width":"512",
    "img_height":"512"
    }

    # response = requests.post(url, json=data, headers={"x-api-key": f"{api_key}"})
    # print(response)
    # image = Image.open(BytesIO(response.content))
    # image.save('new_image.jpg')


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL",  "sqlite:///blog.db")
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

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)