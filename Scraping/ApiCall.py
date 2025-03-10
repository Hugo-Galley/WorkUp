import http.client
import requests
import json
import logging
from config import data as configData

def callJoobleApi(conn,cursor,keyword, location):
    host = configData["Api"]["Jooble"]["Host"]
    key = configData["Api"]["Jooble"]["Key"]
    connection = http.client.HTTPConnection(host)
    headers = {"Content-type": "application/json"}
    keyword = ",".join(keyword)
    body = f'{{ "keywords": "{keyword}", "location": "{location}"}}'
    connection.request('POST', '/api/' + key, body, headers)
    response = connection.getresponse()
    logging.debug(f"{response.status},{response.reason}")
    jsonRespon = response.read().decode('utf-8')
    data = json.loads(jsonRespon)
    logging.info(f"{len(data['jobs'])} Jobs trouvé pour sur Jooble")
    cursor.execute("SELECT COUNT(*) FROM Jobs")
    nbrLineBefore = cursor.fetchone()[0]
    for i in range(len(data["jobs"])):
        try:
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

        except Exception as e:
            logging.error(f"Erreur SQL : {e}")
            conn.rollback()
    cursor.execute("SELECT COUNT(*) FROM Jobs")
    nbrLineAfter = cursor.fetchone()[0]
    return (len(data["jobs"]),nbrLineAfter-nbrLineBefore)

def callAdzunaAPI(conn,cursor,keyword, location):
    keyword = ",".join(keyword)
    params = {
        "app_id": configData["Api"]["Adzuna"]["Id"],
        "app_key": configData["Api"]["Adzuna"]["Key"],
        "results_per_page": 100,
        "what": keyword,
        "where" : location
    }
    response = requests.get(configData["Api"]["Adzuna"]["Host"], params=params)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"{len(data['results'])} Jobs trouvé pour sur Adzuna")
        cursor.execute("SELECT COUNT(*) FROM Jobs")
        nbrLineBefore = cursor.fetchone()[0]
        for i in range(len(data["results"])):
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
                        data["results"][i]["salary_is_predicted"],
                        data["results"][i]["redirect_url"],
                        data["results"][i]["location"]["display_name"],
                        data["results"][i]["description"],
                        data["results"][i]["redirect_url"]
                    )
                )
                conn.commit()

            except Exception as e:
                logging.error(f"Erreur SQL : {e}")
                conn.rollback()
    else:
        logging.error(f"Erreur : {response.status_code}")
    cursor.execute("SELECT COUNT(*) FROM Jobs")
    nbrLineAfter = cursor.fetchone()[0]
    return (len(data["results"]),nbrLineAfter-nbrLineBefore)

def callLaBonneAlteranceApi(conn,cursor,insee,diploma):
    newJob = 0
    host = 'https://labonnealternance-recette.apprentissage.beta.gouv.fr/api/v1/jobsEtFormations'
    params = {
        "romes": "A1202,A1203,A1204,A1301,A1303,A1404,A1405,A1408,A1414,A1416,C1501,C1502,C1504,D1101,D1102,D1104,D1105,D1106,D1202,D1212",
        "caller": "contact@domaine nom_de_societe",
        "latitude": "48.845",
        "longitude": "2.3752",
        "radius": "30",
        "insee": insee,
        "diploma": diploma,
    }
    response = requests.get(host, params=params)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"{len(data['jobs']['partnerJobs']['results'])} Jobs trouvé pour sur la bonne alternance")
        cursor.execute("SELECT COUNT(*) FROM Jobs")
        nbrLineBefore = cursor.fetchone()[0]
        for i in range(len(data["jobs"]["partnerJobs"]["results"])):
            try:
                cursor.execute(
                    """
                    INSERT INTO Jobs (Title, Entreprise, Link, Localisation, Description,Source)
                    SELECT %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM Jobs 
                        WHERE Link = %s
                    )
                    """,
                    (
                        data["jobs"]["partnerJobs"]["results"][i]["title"],
                        data["jobs"]["partnerJobs"]["results"][i]["company"]["name"],
                        data["jobs"]["partnerJobs"]["results"][i]["contact"]["url"],
                        data["jobs"]["partnerJobs"]["results"][i]["place"]["city"],
                        data["jobs"]["partnerJobs"]["results"][i]["job"]["description"],
                        data["jobs"]["partnerJobs"]["results"][i]["job"]["partner_label"],
                        data["jobs"]["partnerJobs"]["results"][i]["contact"]["url"],

                    )
                )
                conn.commit()


            except Exception as e:
                logging.error(f"Erreur SQL : {e}")
                conn.rollback()
        cursor.execute("SELECT COUNT(*) FROM Jobs")
        nbrLineAfter = cursor.fetchone()[0]
        return (len(data["jobs"]["partnerJobs"]["results"]),nbrLineAfter-nbrLineBefore)
