import os
import sys
import psycopg2
from back.fetchData import VertretungsTag


connection = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

offset_1:int = 0
offset_2:int = 1
if len(sys.argv) == 3:
	offset_1 = int(sys.argv[1])
	offset_2 = int(sys.argv[2])


for r in range(offset_1, offset_2):
	v = VertretungsTag()
	v.fetch(r)
	v.format()
	v.writeToDB(connection)

connection.close()