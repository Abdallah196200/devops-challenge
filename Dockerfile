FROM python:latest

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV API_TOKEN=changeme-super-secret
ENV FLASK_DEBUG=1

EXPOSE 5000

CMD python app/main.py
