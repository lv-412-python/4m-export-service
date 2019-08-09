FROM ubuntu:18.04

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt update -y && \
    apt install -y python3 python3-dev python3-pip libssl-dev libffi-dev

COPY ./ ./opt/export-service-repo
WORKDIR /opt/export-service-repo

EXPOSE 5050
RUN make docker-install

ENTRYPOINT ["python3"]
CMD ["setup.py"]
