FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN export ENV_FILE_LOCATION=./.env
COPY . .

EXPOSE 8080
CMD ["python3", "app.py"]
