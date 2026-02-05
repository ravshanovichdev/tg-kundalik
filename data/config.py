import os
from dotenv import load_dotenv

load_dotenv()

botTOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# База данных (MySQL)
mysqlHost = os.getenv("MYSQL_HOST")
mysqlUser = os.getenv("MYSQL_USER")
mysqlPassword = os.getenv("MYSQL_PASSWORD")
mysqlDatabase = os.getenv("MYSQL_DATABASE")

# Логи в группу (опционально)
logsGroupID = int(os.getenv("LOGS_GROUP_ID", '0'))

