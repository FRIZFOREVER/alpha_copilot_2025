FROM node:20-slim AS builder

WORKDIR /app

# Build arguments для переменных окружения Vite
ARG VITE_API_BASE_URL=https://jabkialphacopilot.ru/
ARG VITE_ML_SERVICE_URL=http://localhost:8000/

# Устанавливаем переменные окружения для сборки
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_ML_SERVICE_URL=$VITE_ML_SERVICE_URL

COPY package.json package-lock.json* ./

RUN npm install --legacy-peer-deps

RUN ./node_modules/.bin/tsc --version && \
    ./node_modules/.bin/vite --version

COPY . .

RUN ./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

