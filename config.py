# IPs das impressoras na rede a serem monitoradas
PRINTER_IPS = [
    "10.19.1.178",
    # Adicione mais IPs aqui
]

# Dicionário de OIDs que desejamos monitorar.
# O exemplo abaixo utiliza o OID padrão para o contador total de páginas.
OIDS = {
    "total_counter": "1.3.6.1.2.1.43.10.2.1.4.1.1",
}

# URL da API Laravel onde os dados serão armazenados
API_URL = "http://printer-api.test/api/readings"

# Community String do SNMP (o padrão de leitura na maioria dos dispositivos é 'public')
SNMP_COMMUNITY = "public"

# Intervalo de coleta (polling) em segundos
POLL_INTERVAL = 60
