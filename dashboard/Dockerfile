FROM node:22-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
ENV NODE_ENV=production HOST=0.0.0.0 PORT=3000 DB_FILE=/data/dashboard.sqlite
VOLUME /data
EXPOSE 3000
CMD ["node", "server.js"]
