import requests
from PIL import Image
from io import BytesIO
from flask import Flask, render_template
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

@app.route('/')
def main():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)