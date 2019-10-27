from psycopg2 import connect

conn = connect("dbname=spiderbook user=postgres password=postgres")
c = conn.cursor()

c.close()
conn.close()
