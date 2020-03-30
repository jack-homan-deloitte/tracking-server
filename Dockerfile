FROM python:3.7.6-slim-stretch

RUN useradd -ms /bin/bash tracking

RUN apt-get update \
        && apt-get install -y curl \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install \
        -r requirements.txt \
        gunicorn

USER tracking
WORKDIR /srv/idiet/tracking
COPY idiet idiet

EXPOSE 5000
HEALTHCHECK CMD curl --fail http://localhost:5000/api/hc || exit 1

CMD ["--bind", "0.0.0.0:80", "--workers=4", "idiet.tracking.wsgi:create_app()"]
ENTRYPOINT ["gunicorn"]
