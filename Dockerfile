# Usa l'immagine base di Python
FROM python:3.10-slim

# Crea la directory di lavoro
WORKDIR /app

# Copia requirements.txt ed esegui pip install
COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y libaio1 unzip gzip procps && \
    pip install --no-cache-dir -r requirements.txt

# Copia e installa Oracle Instant Client
COPY oracle_restore/instantclient-basic-linux.x64-23.7.0.25.01.zip /tmp/
RUN unzip /tmp/instantclient-basic-linux.x64-23.7.0.25.01.zip -d /opt/oracle && \
    rm /tmp/instantclient-basic-linux.x64-23.7.0.25.01.zip

# Imposta le variabili d'ambiente per Oracle Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_7
ENV ORACLE_HOME=/opt/oracle/instantclient_23_7

# Copia i file dello script e le cartelle necessarie
COPY restore_and_export.py /app/
COPY data /app/data
COPY output /app/output

# Assicura permessi adeguati per la cartella output
RUN mkdir -p /app/output && chmod -R 777 /app/output

# Esegui lo script Python con dettagli sui log
CMD ["python", "-u", "restore_and_export.py"]
