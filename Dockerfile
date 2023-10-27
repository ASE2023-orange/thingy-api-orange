FROM python:3.10
# For raspberry pi, user python-buster instead of slim-buster

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY . /

WORKDIR /

EXPOSE 8000

CMD ["/bin/sh",  "-c",  "gunicorn -w 1 -b 0.0.0.0:8000 gunicorn_entry:main --worker-class aiohttp.GunicornWebWorker"]