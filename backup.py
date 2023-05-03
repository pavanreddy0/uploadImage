import os
import io
from base64 import encodebytes, b64encode

# import base64
from PIL import Image


import json
from flask import Flask, Response, request, send_file
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from encoder import JSONEncoder

# from flask import Blueprint, Response, request


from dotenv import load_dotenv

load_dotenv(verbose=True)

# specify database configurations
# https://realpython.com/flask-by-example-part-1-project-setup/


app = Flask(__name__)

files_directory = os.getcwd() + "/files"
app.config["UPLOAD_PATH"] = files_directory


@app.route("/")
def index():
    return "Hello World!"


def get_response_image(image_path):
    pil_img = Image.open(image_path, mode="r")  # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format="PNG")  # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode("ascii")  # encode as base64
    return encoded_img


@app.route("/images", methods=["GET"])
def get_images():
    result_files = []
    for sub_dir, dirs, files in os.walk(files_directory):
        result_files = files
    res = []
    print(files)
    for file in result_files:
        file_name = file.split(".")
        if file_name[1] == "myjpg":
            res.append({"file_name": file_name[0] + ".jpg"})
    print(res)
    return res


@app.route("/image/<name>", methods=["GET"])
def get_image(name):
    file_name = name.split(".")
    file = "files/%s" % file_name[0] + ".myjpg"
    res = ""
    with open(file, "rb") as image2string:
        res = b64encode(image2string.read())
        print(res)
    # res = {"data": get_response_image("files/%s" % file_name[0] + ".myjpg")}
    res = {"data": res.decode()}
    return json.dumps(res)


@app.route("/images", methods=["POST"])
def post_images():
    file = request.files["image"]
    print(file)
    print(type(file))
    print(file.filename)
    filename = file.filename.split(".")[0] + ".myjpg"
    file.filename = filename
    # file.save(secure_filename(file.filename))
    file.save("files/" + file.filename)
    return Response(status=200, mimetype="application/json")


# {
#   "dev": {
#     "app_function": "app.app",
#     "aws_region": "us-east-2",
#     "profile_name": "default",
#     "project_name": "uploadimage-bac",
#     "runtime": "python3.9",
#     "s3_bucket": "image-backend",
#     "extra_permissions": [
#       {
#         "Effect": "Allow",
#         "Action": ["rekognition:*"],
#         "Resource": "*"
#       }
#     ]
#   }
# }
