# -------- build --------
FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/cockpit/package*.json ./
RUN npm ci

COPY frontend/cockpit/ ./
RUN npm run build

# -------- produção --------
FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY frontend/cockpit/nginx.conf /etc/nginx/conf.d/default.conf

# copia o dist gerado
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]