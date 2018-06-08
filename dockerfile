FROM python:3

WORKDIR /usr/src/pyrenamer

COPY . /usr/src/pyrenamer

RUN pip install --no-cache-dir guessit imdbpy tvdb_api

ENTRYPOINT ["python", "pyrenamer.py"]
CMD ["--help"]
