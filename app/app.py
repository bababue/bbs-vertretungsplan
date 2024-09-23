import os
from flask import Flask, render_template, request, make_response
import psycopg2
import datetime
from markupsafe import escape



connection = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

cursor = connection.cursor()

app = Flask(__name__)

def fetchSelectedEntries(date, kurs):
    if kurs == "Alle":
        query = """
        SELECT 
            kurs AS Kurs,
            stunde AS Stunde,
            stunde_2 AS Stunde_2,
            raum AS Raum,
            raum_ersatz AS Raum_Ersatz,
            lehrer AS Lehrer,
            lehrer_ersatz AS Lehrer_Ersatz,
            typ AS Typ,
            beschreibung as Beschreibung

        FROM aktuell
        WHERE datum = %s
        ORDER BY Kurs, Stunde;
        """
        cursor.execute(query, [date])
    else:
        query = """
        SELECT 
            kurs AS Kurs, 
            stunde AS Stunde,
            stunde_2 AS Stunde_2,
            raum AS Raum,
            raum_ersatz AS Raum_Ersatz,
            lehrer AS Lehrer,
            lehrer_ersatz AS Lehrer_Ersatz,
            typ AS Typ,
            beschreibung as Beschreibung

        FROM aktuell
        WHERE datum = %s
        AND kurs IN (%s)
        ORDER BY Kurs, Stunde;
        """
        cursor.execute(query, [date, kurs])

    return cursor.fetchall()


@app.route("/", methods=["GET"])
def index():
    cookie_course = request.cookies.get("last_course")
    default_course = "Alle" if cookie_course == None else cookie_course #Set the default course to "Alle" or, if exists, the current cookie value

    default_date = datetime.date.today().strftime("%Y-%m-%d")
    
    return render_template(
        "index.html",
        default_date=default_date,
        default_course=default_course
    )


@app.route("/query", methods=["POST"])
def query():
    # Load both date and course from the post data
    selected_date = escape(request.form["date"])
    selected_course = escape(request.form["kurs"])

    results = fetchSelectedEntries(selected_date, selected_course)

    alle_selected = True if selected_course == "Alle" else False

    resp = make_response(
        render_template("results.html", results=results, alle_selected=alle_selected)
    )
    resp.set_cookie("last_course", value = selected_course, expires=datetime.datetime.now() + datetime.timedelta(days=365))
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=187, debug=True)
