from dotenv import load_dotenv
import os

load_dotenv()

env_config = {
    'SQL_HOST': os.getenv('MYSQL_HOST') or os.getenv('MYSQL_HOST_DEV'),
    'SQL_USER': os.getenv('MYSQL_USER') or os.getenv('MYSQL_USER_DEV'),
    'SQL_PASSWORD': os.getenv('MYSQL_PASSWORD') or os.getenv('MYSQL_PASSWORD_DEV'),
    'SQL_DBNAME': os.getenv('MYSQL_DB') or os.getenv('MYSQL_DB_DEV'),
    'WEB_PORT': os.getenv('WEB_PORT') or os.getenv('WEB_PORT_DEV'),
    'WEB_HOST': os.getenv('WEB_HOST') or os.getenv('WEB_HOST_DEV'),
    'REMOTE_MACHINE_USERNAME': os.getenv('REMOTE_COURSE_USERNAME') or os.getenv('REMOTE_USERNAME_DEV'),
    'REMOTE_MACHINE_PASSWORD': os.getenv('REMOTE_COURSE_PASSWORD') or os.getenv('REMOTE_PASSWORD_DEV'),
    'REMOTE_MACHINE_CSV_FILES_PATH': '/var/tmp/csv_files',
    'REMOTE_MACHINE_IP': '185.164.16.144'
}
