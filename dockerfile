FROM alpine:latest

RUN apk add --update --no-cache build-base python3 python3-dev py3-pip libxml2 libxml2-dev libxslt libxslt-dev

RUN pip3 install guessit tvdb_api imdbpy

WORKDIR /usr/share/pyrenamer

COPY . /usr/share/pyrenamer

ENTRYPOINT ["python3", "pyrenamer.py"]

CMD ["--help"]
