FROM python:3.11 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV PYTHONPATH=/app

COPY --from=requirements-stage /tmp/requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

RUN apt-get update && apt-get -y dist-upgrade

RUN apt install -y netcat-openbsd

COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x entrypoint.sh

COPY ./ /app/


ENTRYPOINT ["sh", "/app/entrypoint.sh"]