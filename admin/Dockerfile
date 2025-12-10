FROM nginx:alpine

WORKDIR /app

COPY default.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /entrypoint.sh

ENV ADMIN_BASE_URL=admin_panel
ENV DOMAIN=localhost

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
