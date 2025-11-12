FROM ollama/ollama:latest

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini curl; \
    rm -rf /var/lib/apt/lists/*

ENV OLLAMA_INFO=0

EXPOSE 11434/tcp

ENTRYPOINT ["tini","--","ollama"]
CMD ["serve"]
