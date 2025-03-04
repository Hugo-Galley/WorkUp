import http.client
import requests
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
            """
            INSERT IGNORE INTO Jobs (Title, Entreprise, Salary, Link, Localisation, Source, Description)
             SELECT %s, %s, %s, %s, %s, %s, %s
             WHERE NOT EXISTS (
                        SELECT 1 FROM Jobs 
                        WHERE Link = %s
                    )
            """,
            (
                    data["jobs"][i]["title"],
                    data["jobs"][i]["company"],
                    data["jobs"][i]["salary"],
                    data["jobs"][i]["link"],
                    data["jobs"][i]["location"],
                    data["jobs"][i]["source"],
                    data["jobs"][i]["snippet"],
                    data["jobs"][i]["link"]
                    )
        )
    conn.commit()

def callAdzunaAPI(keyword, location):
    host = 'https://api.adzuna.com/v1/api/jobs/fr/search/10'
    app_id = 'fc0763e1'
    app_key = '2c708a95c60ac5965edace06b4365f5d'
    keyword = ",".join(keyword)
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 2,
        # "what": keyword,
        # "location0" : location
    }
    response = requests.get(host, params=params)
    if response.status_code == 200:
        data = response.json()
        for i in range(len(data["results"])):
            logging.debug("Executing SQL insert statement")
            try:
                cursor.execute(
                    """
                    INSERT INTO Jobs (Title, Entreprise, Salary, Link, Localisation, Description)
                    SELECT %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM Jobs 
                        WHERE Link = %s
                    )
                    """,
                    (
                        data["results"][i]["title"],
                        data["results"][i]["company"]["display_name"],
                        data["results"][i]["salary_min"],
                        data["results"][i]["redirect_url"],
                        data["results"][i]["location"]["display_name"],
                        data["results"][i]["description"],
                        data["results"][i]["redirect_url"]  # Paramètre pour la condition WHERE NOT EXISTS
                    )
                )
                conn.commit()

            except Exception as e:
                logging.error(f"Erreur SQL : {e}")
                conn.rollback()
    else:
        logging.error(f"Erreur : {response.status_code}")

if __name__ == "__main__":
    try:
        conn = mysql.connector.connect(**configBdd)
        cursor = conn.cursor()

        callJoobleApi(["Science,IT,IA"], "Paris")
        callAdzunaAPI(["It,Data"],"Paris")

        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(e)

