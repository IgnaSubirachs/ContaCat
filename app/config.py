import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://erpuser:erppass@localhost:3306/erpdb"  # quan desenvolupes fora de docker
)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://erpuser:erppass@db:3306/erpdb"  # 'db' és el nom del servei al docker-compose
)
