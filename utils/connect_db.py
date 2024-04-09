import settings
import psycopg2 as pg

postgres = settings.POSTGRES_LOGIN_DETAILS

def connect_db():

    conn = pg.connect(
    host=postgres["hostname"],
    database=postgres["database"],
    user=postgres["username"],
    password=postgres["password"]
    )
    return(conn)
