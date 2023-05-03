# import pymysql
# import sys
# import boto3
import os


# Db Creation
# https://www.youtube.com/watch?v=RerDL93sBdY

DB_TYPE = os.getenv("DB_TYPE")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# try:
#     conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME)
#     cur = conn.cursor()
#     sql = "create database cloudcomputing007"
#     cur.execute(sql)
#     cur.connection.commit()

# except Exception as e:
#     print("Database connection failed due to {}".format(e))

# with open("files/19427.myjpg", "rb") as f:
#     print(type(f))
