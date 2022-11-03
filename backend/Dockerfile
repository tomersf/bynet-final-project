FROM python:3.10.6
WORKDIR '/app'
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y netcat
EXPOSE 5000
COPY . .
CMD ["flask", "run"]