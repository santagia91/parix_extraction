import os
import time
import logging
import psutil
import cx_Oracle
import gzip
import shutil

# Configura il logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/output/script_debug.log"),
        logging.StreamHandler()
    ]
)

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logging.debug(f"Memoria usata: {mem_info.rss / 1024 / 1024:.2f} MB")

# 1. Attesa per Oracle
logging.info("Attesa per garantire che Oracle sia pronto...")
time.sleep(20)
log_memory_usage()

# 2. Decompressione del file
logging.info("Inizio decompressione del file...")
try:
    with gzip.open('/app/data/dris_20250114.dmp.gz', 'rb') as f_in:
        with open('/app/data/dris_20250114.dmp', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    logging.info("Decompressione completata.")
except Exception as e:
    logging.error(f"Errore durante la decompressione: {e}")
    exit(1)

log_memory_usage()

# 3. Connessione a Oracle
logging.info("Connessione a Oracle...")
dsn_tns = cx_Oracle.makedsn(os.getenv('ORACLE_HOST'), os.getenv('ORACLE_PORT'), service_name=os.getenv('ORACLE_SERVICE'))
try:
    connection = cx_Oracle.connect(user=os.getenv('ORACLE_USER'), password=os.getenv('ORACLE_PASSWORD'), dsn=dsn_tns)
    logging.info("Connessione a Oracle riuscita.")
except cx_Oracle.DatabaseError as e:
    logging.error(f"Errore durante la connessione a Oracle: {e}")
    exit(1)

log_memory_usage()

# 4. Esecuzione del restore
logging.info("Inizio ripristino del database...")
try:
    # Esempio di comando impdp — modifica secondo le tue esigenze
    os.system("impdp system/oracle@//oracle:1521/FREEPDB1 directory=DATA_PUMP_DIR dumpfile=dris_20250114.dmp")
    logging.info("Ripristino completato.")
except Exception as e:
    logging.error(f"Errore durante il ripristino: {e}")
    exit(1)

log_memory_usage()

# 5. Estrarre la lista delle tabelle
logging.info("Estrazione della lista delle tabelle...")
try:
    cursor = connection.cursor()
    cursor.execute("SELECT table_name FROM all_tables WHERE owner = 'SYSTEM'")
    tables = cursor.fetchall()
    with open("/app/output/tables_list.csv", "w") as f:
        for table in tables:
            f.write(f"{table[0]}\n")
    logging.info(f"Numero di tabelle trovate: {len(tables)}")
except cx_Oracle.DatabaseError as e:
    logging.error(f"Errore durante l'estrazione delle tabelle: {e}")
    exit(1)

log_memory_usage()

logging.info("Script completato con successo!")
