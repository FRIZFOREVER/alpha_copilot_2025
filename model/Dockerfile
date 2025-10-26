FROM ollama/ollama:latest

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini curl; \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 11434/tcp

ENTRYPOINT ["tini","--","/usr/local/bin/entrypoint.sh"]

CMD ["serve"]
