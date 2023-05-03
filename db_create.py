import os
from functools import wraps

from dotenv import load_dotenv
from flask import Response, g
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv(verbose=True)


DB_TYPE = os.getenv("DB_TYPE")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# DB_HOST = "127.0.0.1"
# DB_PORT = 3306
# DB_USER = "root"
# DB_NAME = "pavanreddy"
# DB_PASS = "root"


# DB_TYPE = "MySQL"
# DB_HOST = "cc.capygdctxp0y.us-east-2.rds.amazonaws.com"
# DB_PORT = "3306"
# DB_USER = "pavanreddy"
# DB_NAME = "cloudcomputing007"
# DB_PASS = "DbBwXbhw8bJ15D5asLO1"
# configure the SQLite database, relative to the app instance folder

db_url = URL(
    "mysql+pymysql",
    DB_USER,
    DB_PASS,
    DB_HOST,
    DB_PORT,
    DB_NAME,
)


engine = create_engine(db_url)

# session = scoped_session(sessionmaker(bind=engine))


def db_required():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            res = None

            class Sess:
                pass

            g.sess = Sess()

            setattr(g.sess, "db_session", scoped_session(sessionmaker(bind=engine)))

            try:
                res = f(*args, **kwargs)
            except Exception as e:
                print(
                    f"<Exception Occurred : {e}>\nCleaning Database connection...!!! "
                )
                return Response(status=500)

            g.sess.db_session.close()

            del g.sess

            return res

        return wrapped

    return decorator
