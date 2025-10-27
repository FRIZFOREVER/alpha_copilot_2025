FROM ollama/ollama:latest

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini curl; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ollama
COPY .env /opt/ollama/.env
COPY model/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENV OLLAMA_ENV_FILE=/opt/ollama/.env

EXPOSE 11434/tcp

ENTRYPOINT ["tini","--","/usr/local/bin/entrypoint.sh"]

CMD ["serve"]
