FROM python:3.7-alpine
WORKDIR /app
ADD . /app
EXPOSE 8000
RUN pip install -r requirements.txt
CMD ["gunicorn", "server:app"]
