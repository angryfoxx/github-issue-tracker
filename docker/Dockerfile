FROM python:3.12

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y netcat-traditional postgresql-client-15 bash
RUN pip install --upgrade pip wheel setuptools
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
ADD . /code

ENTRYPOINT ["/code/docker/entrypoint.sh"]
