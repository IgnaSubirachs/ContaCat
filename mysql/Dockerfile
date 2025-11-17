FROM mysql:8.0

# Variables per defecte (pots canviar-les o sobreescriure-les al docker-compose)
ENV MYSQL_ROOT_PASSWORD=root \
    MYSQL_DATABASE=erpdb \
    MYSQL_USER=erpuser \
    MYSQL_PASSWORD=erppass

# Scripts SQL que s'executaran automàticament al primer arrenc
COPY init.sql /docker-entrypoint-initdb.d/
