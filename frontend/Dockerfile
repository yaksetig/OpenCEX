FROM nginx:alpine

WORKDIR /app

COPY default.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh

ENV DOMAIN=localhost
ENV ADMIN_BASE_URL=admin_panel

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
