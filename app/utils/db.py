import os

from dotenv import load_dotenv

from sqlalchemy.engine import URL

load_dotenv()

db_url = URL.create(
    os.getenv('DB_DRIVER'),
    username=os.getenv('USERNAME'),
    password=os.getenv('PASSWORD'),   # raw password, no encoding needed
    host=os.getenv('HOST'),
    port=os.getenv('PORT'),
    database=os.getenv('DATABASE'),
)

# os.getenv('DATABASE_URL')
# USERNAME="dba_etv"
# PASSWORD="Tav18%Etv@03!"
# HOST="localhost"
# PORT=3306
# DATABASE="be_aware"