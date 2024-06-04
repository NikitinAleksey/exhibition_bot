FROM python:3.9.18-slim-bookworm

WORKDIR /app

COPY . .

RUN python -m pip install -r requirements.txt

RUN pip install google-api-core google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib googleapis-common-protos

ENTRYPOINT ["python", "bot.py"]

EXPOSE 5555