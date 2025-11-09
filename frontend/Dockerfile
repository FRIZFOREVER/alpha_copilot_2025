# Stage 1: Build
FROM node:20-slim AS builder

WORKDIR /app

# Build argument for API URL
ARG VITE_API_URL=http://localhost:8080/
ENV VITE_API_URL=$VITE_API_URL

# Copy package files first for better Docker layer caching
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies for build)
RUN npm install --legacy-peer-deps

# Verify TypeScript and Vite are installed
RUN ./node_modules/.bin/tsc --version && \
    ./node_modules/.bin/vite --version

# Copy source code and config files
COPY . .

# Build the application using direct paths to binaries
RUN ./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build

# Stage 2: Production
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

