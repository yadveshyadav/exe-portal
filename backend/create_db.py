import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_postgres():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='1234',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'exe_portal'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE exe_portal')
            print('[+] Database "exe_portal" created successfully in PostgreSQL!')
        else:
            print('[*] Database "exe_portal" already exists in PostgreSQL.')
        cur.close()
        conn.close()
    except Exception as e:
        print('[-] PostgreSQL Error:', e)

if __name__ == '__main__':
    init_postgres()
