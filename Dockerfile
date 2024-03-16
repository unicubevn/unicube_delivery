#FROM debian:bullseye-slim
FROM python:3.11.4-slim-bullseye
MAINTAINER The Bean Family <community@thebeanfamily.org>

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8
ENV TZ=UTC

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        libldap2-dev \
        libsasl2-dev \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
        libtiff5-dev \
        libopenjp2-7-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        xfonts-75dpi \
        node-less \
        npm \
        python3-num2words \
        python3-pdfminer \
        python3-pip \
        python3-phonenumbers \
        python3-pyldap \
        python3-qrcode \
        python3-renderpm \
        python3-setuptools \
        python3-slugify \
        python3-vobject \
        python3-watchdog \
        python3-xlrd \
        python3-xlwt \
        python3-ldap \
        python3-odf \
        python3-magic \
        gcc \
        g++ \
        make \
        nano \
        xz-utils

# install wkhtmltox lib
RUN curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss \
    && npm install -g vietqr-payment

# Install Odoo
ENV ODOO_VERSION 17.0
ARG ODOO_RELEASE=20231216
ARG ODOO_SHA=e7ddf8de9873c66ef887c5bf23b3698673a1ba35
RUN adduser odoo
RUN mkdir -p /mnt/app \
    && chown -R odoo /mnt/app
COPY ./app /mnt/app/
COPY ../requirements.txt /mnt/app/
RUN pip install setuptools wheel \
    && pip install -r /mnt/app/requirements.txt \
    && pip install -e /mnt/app/

# Copy entrypoint script and Odoo configuration file
WORKDIR /mnt/app/
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons \
    && mkdir -p /mnt/shared-addons \
    && chown -R odoo /mnt/shared-addons \
    && chown odoo /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && mkdir -p /var/lib/odoo \
    && chown -R odoo /var/lib/odoo
VOLUME ["/var/lib/odoo", "/mnt/extra-addons","/mnt/shared-addons","/etc/odoo"]

# Expose Odoo services
EXPOSE 8070 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

COPY wait-for-psql.py /wait-for-psql.py
RUN chown odoo /wait-for-psql.py \
    && chmod +x /wait-for-psql.py

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
