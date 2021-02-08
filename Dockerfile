ARG PYTHON_VERSION

FROM python:$PYTHON_VERSION-alpine

MAINTAINER "Guillaume M <marmorag>"

ENV LD_LIBRARY_PATH /usr/local/lib:/usr/lib
ENV MUSL_LOCPATH="/usr/share/i18n/locales/musl"

RUN apk --no-cache add -q git build-base gnupg linux-headers xz musl-locales musl-locales-lang \
    > /dev/null && \
    # configure locale
#    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
#    locale-gen && \
    # remove caches
    rm -rf /var/cache/apk/*

WORKDIR /app
COPY . .

#ENV LC_ALL fr_FR.UTF-8
#ENV LANG fr_FR.UTF-8
#ENV LANGUAGE fr_FR:fr

RUN pip install -r requirements.txt && \
    rm -rf /root/.cache/pip/*

CMD ["python", "-u", "main.py"]
