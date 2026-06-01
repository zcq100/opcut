FROM python:3.12-slim-bookworm as opcut-base
WORKDIR /opcut
RUN apt update -y && \
    apt install -y pkg-config gcc libcairo2-dev && \
    python3 -m venv /opt/opcut

FROM opcut-base as opcut-build
WORKDIR /opcut
RUN apt install -y nodejs npm git
COPY . .
RUN /opt/opcut/bin/pip install -r requirements.pip.txt && \
    /opt/opcut/bin/doit clean_all && \
    /opt/opcut/bin/doit

FROM opcut-base as opcut-run
WORKDIR /opcut
COPY --from=opcut-build /opcut/build/py/*.whl .
RUN /opt/opcut/bin/pip install *.whl && \
    rm -r /opcut
EXPOSE 8080
CMD ["/opt/opcut/bin/opcut", "server"]
