import mysql.connector
import logging
import config
import ApiCall

config.setupLog()

if __name__ == "__main__":
    try:
        conn = mysql.connector.connect(**config.configBdd)
        cursor = conn.cursor()

        (nbrGetJobsJooble,nbrNewJobsJooble) = ApiCall.callJoobleApi(conn,cursor,["Science,IT,IA"], "Paris")
        (nbrGetJobsAdzuna,nbrNewJobsAdzuna) = ApiCall.callAdzunaAPI(conn,cursor,["It,Data"],"75000")
        (nbrGetJobsLba,nbrNewJobsLba) = ApiCall.callLaBonneAlteranceApi(conn,cursor,"75056","7 (Master, titre ingénieur...)")

        cursor.close()
        conn.close()
        logging.info("Fin du passage")
        logging.info(f"Nombre de jobs récupéré : {nbrGetJobsJooble+nbrGetJobsAdzuna+nbrGetJobsLba}")
        logging.info(f"Nombre de nouveau jobs récuperé : {nbrNewJobsJooble+nbrNewJobsLba+nbrNewJobsAdzuna}")
    except Exception as e:
        logging.error(e)

