FROM python:3.7-alpine
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "server:app"]
