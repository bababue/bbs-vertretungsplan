def updateCourses(connection):
	cursor = connection.cursor()

	f = open("app/templates/courses.html", "w")

	cursor.execute(
		"""
		SELECT DISTINCT kurs FROM aktuell
		ORDER BY kurs;  
		"""
	)

	for r in cursor.fetchall():
		element = f'<option {{% if default_course == "{r[0]}" %}}selected{{% endif %}} value="{r[0]}">{r[0]}</option>\n'
		f.write(element)
	f.close()