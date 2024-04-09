#import ElGatoBot.settings
import psycopg as pg

def connect_db(postgres):
    conn = pg.connect(
        host=postgres["hostname"],
        dbname=postgres["database"],
        user=postgres["username"],
        password=postgres["password1"]
    )
    return(conn)
