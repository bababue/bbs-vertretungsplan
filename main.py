from dotenv import load_dotenv
import os
import sys
import psycopg2
from back.fetchData import VertretungsTag
from back.updateCourses import updateCourses

load_dotenv()

connection = psycopg2.connect(
	database=os.getenv("pg_database"),
	host=os.getenv("pg_host"),
	port=os.getenv("pg_port"),
	user=os.getenv("pg_user"),
	password=os.getenv("pg_password")
)

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

updateCourses(connection)

connection.close()