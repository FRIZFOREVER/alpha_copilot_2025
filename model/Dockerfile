FROM ollama/ollama:latest

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini curl dos2unix; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ollama

COPY .env /opt/ollama/.env
COPY model/entrypoint.sh /usr/local/bin/entrypoint.sh

# Конвертация перевода строк в Unix-формат
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

ENV OLLAMA_ENV_FILE=/opt/ollama/.env

EXPOSE 11434/tcp

ENTRYPOINT ["tini","--","/usr/local/bin/entrypoint.sh"]
CMD ["serve"]
