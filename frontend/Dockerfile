FROM node:22-alpine AS base
WORKDIR /app
COPY package*.json .

FROM base AS dev
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS builder
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine AS prod
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
