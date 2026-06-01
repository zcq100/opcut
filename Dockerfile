FROM python:3.12-alpine3.20 AS opcut-base
WORKDIR /opcut
RUN apk add --no-cache cairo && \
    python3 -m venv /opt/opcut

FROM opcut-base AS opcut-build
WORKDIR /opcut
RUN apk add --no-cache build-base pkgconf cargo cairo-dev nodejs npm
COPY requirements.pip.txt package.json package-lock.json node_modules.patch ./
RUN /opt/opcut/bin/pip install --no-cache-dir -r requirements.pip.txt && \
    npm install && \
    patch -p1 < node_modules.patch
COPY . .
RUN /opt/opcut/bin/doit clean_all && \
    /opt/opcut/bin/doit && \
    /opt/opcut/bin/pip wheel -w /opcut/wheels /opcut/build/py/*.whl

FROM opcut-base AS opcut-run
WORKDIR /opcut
COPY --from=opcut-build /opcut/wheels /opcut/wheels
COPY --from=opcut-build /opcut/build/py/*.whl .
RUN /opt/opcut/bin/pip install --no-cache-dir --no-index --find-links /opcut/wheels *.whl && \
    rm -rf /opcut /opcut/wheels /root/.cache
EXPOSE 8080
CMD ["/opt/opcut/bin/opcut", "server"]
