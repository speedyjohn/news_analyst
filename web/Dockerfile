FROM node:22-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Штатный энтрипоинт nginx прогоняет envsubst по /etc/nginx/templates/*.template
# и кладёт результат в /etc/nginx/conf.d/. Фильтр ограничивает подстановку тремя
# нашими переменными, иначе envsubst съел бы $uri, $host, $upstream и $remote_addr.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.d/15-resolver.envsh /docker-entrypoint.d/15-resolver.envsh
RUN chmod +x /docker-entrypoint.d/15-resolver.envsh
ENV NGINX_ENVSUBST_FILTER="^(PORT|API_UPSTREAM|NGINX_RESOLVER)$"

# Значения по умолчанию — под docker compose, где сервис API зовётся api.
# На Railway обе переменные задаются в настройках сервиса.
ENV PORT=80
ENV API_UPSTREAM=http://api:8000
