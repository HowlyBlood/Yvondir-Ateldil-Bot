ARG PYTHON_VERSION

FROM python:$PYTHON_VERSION-buster

MAINTAINER "Guillaume M <marmorag>"

WORKDIR /app
COPY . .

RUN apt-get update && \
    # basic deps
    apt-get install -y -qq git build-essential locales \
    # voice support
    # libffi-dev libsodium-dev libopus-dev ffmpeg \
    > /dev/null && \
    # configure locale
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    # update pip, install Cython, pytest, youtube-dl
    pip install -U pip Cython -q --retries 30 && \
    # remove caches
    rm -rf /root/.cache/pip/* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests \) \) \
            -o \
            \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
        \) -exec rm -rf '{}' +

ENV LC_ALL fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR:fr

RUN pip install -r requirements.txt

CMD ["python", "-u", "main.py"]
