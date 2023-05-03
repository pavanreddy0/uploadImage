import datetime
import json
import os
from base64 import b64encode
from datetime import date, datetime, timedelta

from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, Response, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from requests.exceptions import HTTPError

from boto_client import Boto
from db_create import db_required, g
from models import Images, User

# connect(db="FAU", host="localhost", port=27017)
# MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True)

# https://www.youtube.com/watch?v=3sQhVKO5xAA
# https://www.youtube.com/watch?v=zjuItRMUAcM
# https://github.com/yeshwanthlm/YouTube/blob/main/flask-on-aws-ec2.md
# https://www.youtube.com/watch?v=ct1GbTvgVNM
# https://www.youtube.com/watch?v=goToXTC96Co

# https://jjn5qako7g.execute-api.us-east-2.amazonaws.com/dev
# Deployment -> https://www.youtube.com/watch?v=Vl5wroVmSuk

# login
# https://dev.to/paurakhsharma/flask-rest-api-part-3-authentication-and-authorization-5935

load_dotenv(verbose=True)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

app = Flask(__name__)
# app.config.from_envvar("ENV_FILE_LOCATION")
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
cors = CORS(app)


jwt = JWTManager(app)
# Make session for my_sql connection
# g.sess.db_session = session()

# Intialize the Boto Client
boto = Boto()


@app.route("/", methods=["GET"])
def hello():
    return "Hello"


def validate_email(email):
    user = g.sess.db_session.query(User).filter(User.email == email).first()
    print(user)
    if user is None:
        return True
    print("Not none")
    raise Exception("Email already registered!")


def JSONEncoder(obj):
    if isinstance(obj, datetime):
        # return obj.strftime("%d-%b-%Y %I:%M:%S %p")
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, date):
        return obj.strftime("%d-%b-%Y")
    elif isinstance(obj, timedelta):
        return str(obj)
    elif isinstance(obj, float):
        return float(obj)
    elif isinstance(obj, int):
        return int(obj)


# def validate_uname(uname):
#     if g.sess.db_session.query(User).filter(User.username == uname).first():
#         raise Exception("Username already taken!")


@app.route("/signup", methods=["POST"])
@db_required()
def signup():
    body = request.json
    email = body.get("email")
    password = body.get("password")
    print("Email ", email)
    print("password ", password)
    if email == None or password == None or len(email) == 0 or len(password) == 0:
        return Response(json.dumps(), status=500, mimetype="application/json")
    try:
        validate_email(email)
    except Exception as e:
        return Response(
            json.dumps(str(e)),
            status=500,
            mimetype="application/json",
        )
    try:
        user = User(email=email, password=password)
        user.hash_password()
        g.sess.db_session.add(user)
        g.sess.db_session.flush()

        g.sess.db_session.commit()
        return Response(status=201, mimetype="application/json")
    except Exception as e:
        return Response(
            json.dumps(e, default=JSONEncoder), status=500, mimetype="application/json"
        )


@app.route("/login", methods=["POST"])
@db_required()
def login():
    body = request.json
    email = body.get("email")
    password = body.get("password")
    try:
        validate_email(email)
        return Response(
            json.dumps({"User not registered"}, default=JSONEncoder),
            status=400,
            mimetype="application/json",
        )
    except Exception as e:
        print(e)
    try:
        user = g.sess.db_session.query(User).filter(User.email == email).first()
        authorised = user.check_password(password)
        if not authorised:
            return Response(
                json.dumps({"Incorrect password"}),
                status=401,
                mimetype="application/json",
            )
        expires = timedelta(days=7)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        data = {"token": access_token}
        return Response(
            json.dumps(data, default=JSONEncoder),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": "Failed login"}, default=JSONEncoder),
            status=500,
            mimetype="application/json",
        )


@app.route("/images", methods=["GET"])
@jwt_required()
@db_required()
def get_images():
    res = []
    current_user = int(get_jwt_identity())
    print(current_user)
    try:
        # images = g.sess.db_session.query(Images).filter(Images.user_id == current_user).all()
        user = g.sess.db_session.query(User).filter(User.id == current_user).first()
        images = user.images
        for image in images:
            file_name = image.name.split(".")
            res.append({"file_name": file_name[0] + ".jpg"})
        return Response(
            json.dumps(res, default=JSONEncoder),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        return Response(
            json.dumps({"message": "Failed to get Images"}),
            status=500,
            mimetype="application/json",
        )


@app.route("/image/<name>", methods=["GET"])
@jwt_required()
@db_required()
def get_image(name):
    file_name = name.split(".")
    db_file_name = file_name[0] + ".myjpg"
    current_user = int(get_jwt_identity())

    try:
        image = (
            g.sess.db_session.query(Images).filter(Images.name == db_file_name).first()
        )
        if image is None:
            return Response(
                json.dumps({"message": "Image Not Found"}),
                status=404,
                mimetype="application/json",
            )

        user = image.user

        logged_in_user = (
            g.sess.db_session.query(User).filter(User.id == current_user).first()
        )
        user = image.user

        images = logged_in_user.images
        image_ids = [image.id for image in images]
        if image.id not in image_ids or user.id != current_user:
            raise Exception("Image does not belong to this user.")

    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": "Failed to get images"}, default=JSONEncoder),
            status=401,
            mimetype="application/json",
        )

    try:
        file = boto.download_file(db_file_name)
        # image_str = b64encode(file.read()).decode() ## read isn not working with BytesIO
        image_str = b64encode(file.getvalue()).decode()
        res = {
            "id": image.id,
            "data": image_str,
            "size": round(image.size / 1000),
        }
        return Response(json.dumps(res), 200, mimetype="application/json")
    except Exception as e:
        return Response(
            json.dumps({"message": "Failed to download Image"}),
            status=500,
            mimetype="application/json",
        )


@app.route("/images", methods=["POST"])
@jwt_required()
@db_required()
def post_images():
    file = request.files["image"]
    data = request.form
    filename = file.filename.split(".")[0] + ".myjpg"
    content_type = file.mimetype

    current_user = int(get_jwt_identity())
    try:
        image = Images(name=filename, size=data.get("size"), user_id=current_user)
        g.sess.db_session.add(image)
        g.sess.db_session.flush()

        boto.upload_file(filedata=file, filename=filename, content_type=content_type)
        g.sess.db_session.commit()
        return Response(status=201, mimetype="application/json")
    except Exception as e:
        print(e)
        g.sess.db_session.rollback()
        return Response(
            json.dumps({500, "Internal Server Error."}, default=JSONEncoder),
            status=500,
            mimetype="application/json",
        )


@app.route("/image/<id>", methods=["DELETE"])
@jwt_required()
@db_required()
def delete_reservation(id):
    """Delete a image"""
    current_user = int(get_jwt_identity())
    try:
        # delete file from storage
        image = g.sess.db_session.query(Images).filter(Images.id == id).first()
        if image is None:
            return Response(
                json.dumps({"message": "Image Not Found"}),
                status=404,
                mimetype="application/json",
            )

        logged_in_user = (
            g.sess.db_session.query(User).filter(User.id == current_user).first()
        )
        user = image.user

        images = logged_in_user.images
        image_ids = [image.id for image in images]

        if image.id not in image_ids or user.id != current_user:
            raise Exception("Image does not belong to this user.")

        g.sess.db_session.delete(image)
        g.sess.db_session.flush()

        file_name = image.name.split(".")
        db_file_name = file_name[0] + ".myjpg"

        boto.delete_files([db_file_name])

        g.sess.db_session.commit()
        return Response(status=202, mimetype="application/json")

    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": "Failed to delete image"}, default=JSONEncoder),
            500,
            mimetype="application/json",
        )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
