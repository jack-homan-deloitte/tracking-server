FROM python:3.7.6-slim-stretch

RUN useradd -u 1000 -ms /bin/bash tracking

RUN apt-get update \
        && apt-get install -y curl \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /
RUN pip install \
        -r /requirements.txt \
        gunicorn

USER tracking
WORKDIR /srv/idiet/tracking
COPY --chown=tracking idiet idiet
COPY --chown=tracking test-requirements.txt /
COPY --chown=tracking tests /tests
RUN rm /tests/test_system.py

EXPOSE 8080
HEALTHCHECK CMD curl --fail http://localhost:8000/api/hc || exit 1

ENV IDIET_TRACKING_SECRET ""

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers=4", "idiet.tracking.wsgi:app"]
