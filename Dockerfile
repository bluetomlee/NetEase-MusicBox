FROM ubuntu:14.04

# Install Python.
RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/*

ADD ./apis /apis

WORKDIR /apis

RUN pip install -r requirements.txt
EXPOSE 80

ENTRYPOINT ["python","index.py"]