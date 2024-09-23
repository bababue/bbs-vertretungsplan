import requests
from datetime import datetime
import html
import re

current_date = int(datetime.now().strftime("%Y%m%d"))

request_config = {
    "url": "https://kephiso.webuntis.com/WebUntis/monitor/substitution/data",
    "params": {"school": "BBS Friesoythe"},
    "headers": {"content-type": "application/json"},
    "json_data": {
        "formatName": "Vertretung heute",
        "schoolName": "BBS Friesoythe",
        "date": current_date,
        "dateOffset": 0,
        "strikethrough": True,
        "mergeBlocks": True,
        "showOnlyFutureSub": True,
        "showBreakSupervisions": False,
        "showTeacher": True,
        "showClass": False,
        "showHour": True,
        "showInfo": True,
        "showRoom": True,
        "showSubject": False,
        "groupBy": 1,
        "hideAbsent": True,
        "departmentIds": [],
        "departmentElementType": -1,
        "hideCancelWithSubstitution": True,
        "hideCancelCausedByEvent": False,
        "showTime": False,
        "showSubstText": True,
        "showAbsentElements": [
            1,
            2,
        ],
        "showAffectedElements": [
            1,
            2,
        ],
        "showUnitTime": True,
        "showMessages": True,
        "showStudentgroup": False,
        "enableSubstitutionFrom": True,
        "showSubstitutionFrom": 1700,
        "showTeacherOnEvent": False,
        "showAbsentTeacher": True,
        "strikethroughAbsentTeacher": True,
        "activityTypeIds": [],
        "showEvent": False,
        "showCancel": True,
        "showOnlyCancel": False,
        "showSubstTypeColor": False,
        "showExamSupervision": False,
        "showUnheraldedExams": False,
    }
} 


class VertretungsTag:
    def fetch(self, offset: int):
        request_config["json_data"]["dateOffset"] = offset

        response = requests.post(
            request_config["url"],
            params=request_config["params"],
            headers=request_config["headers"],
            json=request_config["json_data"],
        )

        if response.status_code == 200:
            json_response = response.json()

            #If response contains content of next date, change date to that
            if json_response["payload"]["showingNextDate"] == True:
                json_response["payload"]["date"] = json_response["payload"]["nextDate"]

            print(f'Fetched {len(json_response["payload"]["rows"])} entries, Date: {json_response["payload"]["date"]}')

            self.response = json_response

        else:
            print(f"Fetch unsucessful, error {str(response.status_code)}")
            self.response = None


    class VertretungsEintrag:
        def __init__(self, item) -> None:
            self.kurs = item["group"]

            remove_html_tags = re.compile(r"<.*?>")  # Regex for removing html tags
            typ_escaped = html.unescape(item["data"][3]) #Create a varirable for the escaped "Typ"

            stunde = item["data"][0]
            if len(stunde) == 1:
                self.stunde = int(stunde)
                self.stunde2 = None
            if len(stunde) >= 3:
                self.stunde = int(stunde[0])
                self.stunde2 = int(stunde[-1])
            
            regex_original = re.compile(r"[^\(\)]+") 
            regex_ersatz = re.compile(r"(?<=\().+?(?=\))")

            cleaned_raum = re.sub(remove_html_tags, "", item["data"][1])

            if cleaned_raum.count("(") == 0:
                self.raum = cleaned_raum
                self.raum_ersatz = None
            elif cleaned_raum.count("(") == 1:
                 self.raum = re.findall(regex_original, cleaned_raum)[0].rstrip()
                 self.raum_ersatz = re.findall(regex_ersatz, cleaned_raum)[0]
            elif "Entfall" in typ_escaped or "Verlegung nach" in typ_escaped:
                self.raum= cleaned_raum
                self.raum_ersatz = "---"
            else:
                self.raum = cleaned_raum
                self.raum_ersatz = None

            cleaned_lehrer = re.sub(remove_html_tags, "", item["data"][2])

            if cleaned_lehrer.count("(") > 1:
                self.lehrer = cleaned_lehrer
                self.lehrer_ersatz = None
            # elif cleaned_lehrer.count("(") == 1:
            #     self.lehrer = re.findall(regex_original, cleaned_lehrer)[0].rstrip()
            #     self.lehrer_ersatz = re.findall(regex_ersatz, cleaned_lehrer)[0]
            elif "Entfall" in typ_escaped or "Verlegung nach" in typ_escaped:
                self.lehrer = cleaned_lehrer
                self.lehrer_ersatz = "---"
            else:
                self.lehrer = cleaned_lehrer
                self.lehrer_ersatz = None

            if item["data"][3] != "":
                self.typ = typ_escaped
            else:
                self.typ = None

            if item["data"][4] != "":
                self.beschreibung = html.unescape(item["data"][4])
            else:
                self.beschreibung = None


    def format(self):
        if self.response == None:
            raise TypeError("Response cannot be None")

        self.datum = datetime.strptime(str(self.response["payload"]["date"]), "%Y%m%d").strftime("%Y-%m-%d")

        self.items = []

        for item in self.response["payload"]["rows"]:
            formattedItem = self.VertretungsEintrag(item)
            self.items.append(formattedItem)


    def writeToDB(self, connection):
        cursor = connection.cursor()

        cursor.execute(
            f"""
            DELETE FROM aktuell
            WHERE datum = '{self.datum}';
            """
            )

        for item in self.items:
            query = """
                    INSERT INTO aktuell (datum, stunde, stunde_2, kurs, raum, raum_ersatz, lehrer, lehrer_ersatz, typ, beschreibung)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
            values = [
                    self.datum,
                    item.stunde,
                    item.stunde2,
                    item.kurs,
                    item.raum,
                    item.raum_ersatz,
                    item.lehrer,
                    item.lehrer_ersatz,
                    item.typ,
                    item.beschreibung
                    ]
        cursor.execute(query, values)

        connection.commit()
