FROM python:3.8-alpine
LABEL Author="jon4hz" 
LABEL version="1.0"
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev postgresql-dev python3-dev openssl-dev libffi-dev g++ cargo
RUN pip install --upgrade pip &&\ 
    pip install --no-cache-dir -r requirements.txt
COPY tartis ./tartis
COPY test/channel_signals/config.py test/channel_signals/channel_bot.py ./
RUN sed -i 's/localhost/db/g' config.py
RUN chown -R 1000. . *
USER 1000
CMD [ "python", "-u", "channel_bot.py" ]