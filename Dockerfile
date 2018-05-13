FROM python:3.5-jessie

WORKDIR /Flashfood

ADD . /Flashfood

RUN pip3 install -r requirements.txt

EXPOSE 4000

ENV NAME redpython

CMD ["python", "server.py"]
