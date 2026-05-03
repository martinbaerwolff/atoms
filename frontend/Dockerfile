# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS dev

WORKDIR /app

# Faster reinstalls when only sources change.
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
