import http.client
import json
import mysql.connector
import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        handler,
        logging.FileHandler("app.log", mode="a")
    ]
)
configBdd = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "WorkUp",
    "port": 8889
}

def callJoobleApi(keyword, location):
    host = 'fr.jooble.org'
    key = '1744f78f-86ef-4e96-a21b-a3b465e6efbb'
    connection = http.client.HTTPConnection(host)
    headers = {"Content-type": "application/json"}
    keyword = ",".join(keyword)
    body = f'{{ "keywords": "{keyword}", "location": "{location}"}}'
    connection.request('POST', '/api/' + key, body, headers)
    response = connection.getresponse()
    logging.debug(f"{response.status},{response.reason}")
    jsonRespon = response.read().decode('utf-8')
    data = json.loads(jsonRespon)
    for i in range(len(data["jobs"])):
        cursor.execute(
            "INSERT IGNORE INTO Jobs (Title, Entreprise, Salary, Link, Localisation, Source, Description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                    data["jobs"][i]["title"],
                    data["jobs"][i]["company"],
                    data["jobs"][i]["salary"],
                    data["jobs"][i]["link"],
                    data["jobs"][i]["location"],
                    data["jobs"][i]["source"],
                    data["jobs"][i]["snippet"]
                    )
        )
    conn.commit()

try:
    conn = mysql.connector.connect(**configBdd)
    cursor = conn.cursor()

    print(callJoobleApi(["Science,IT,IA"], "Paris"))

    cursor.close()
    conn.close()
except Exception as e:
    print(e)

