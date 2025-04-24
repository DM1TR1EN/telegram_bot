FROM nginx:1.25-alpine

# Устанавливаем временные директории и настраиваем права доступа
RUN mkdir -p /tmp/client_body /tmp/proxy /tmp/fastcgi /tmp/uwsgi /tmp/scgi \
    && chown -R nginx:nginx /tmp/client_body /tmp/proxy /tmp/fastcgi /tmp/uwsgi /tmp/scgi \
    && chmod -R 777 /tmp/client_body /tmp/proxy /tmp/fastcgi /tmp/uwsgi /tmp/scgi \
    && chmod -R 777 /var/cache/nginx /var/log/nginx /var/run

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Запускаем как пользователя nginx
USER nginx

CMD ["nginx", "-g", "daemon off;"] 