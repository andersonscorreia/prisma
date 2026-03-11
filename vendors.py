# =====================================================
# VENDORS / Mapeamento de OIDs
# =====================================================
# Copie os dicionários completos do seu 'impressoras.py' original para cá.
# Abaixo estão as estruturas de exemplo baseadas no código fornecido.

canon = {
    "contador": "1.3.6.1.2.1.43.10.2.1.4.1.1",
    "tempo_ligada": "1.3.6.1.2.1.1.3.0",
    "N_S": "1.3.6.1.2.1.43.5.1.1.17.1",
    "menssagem_painel": "1.3.6.1.2.1.43.16.5.1.2.1.1",
    "toner_atual": "1.3.6.1.2.1.43.11.1.1.9.1.1",
    "toner_full": "1.3.6.1.2.1.43.11.1.1.8.1.1"
}

richo = {
    "contador": "1.3.6.1.2.1.43.10.2.1.4.1.1",
    "tempo_ligada": "1.3.6.1.2.1.1.3.0",
    "N_S": "1.3.6.1.2.1.43.5.1.1.17.1",
    "menssagem_painel": "1.3.6.1.2.1.43.16.5.1.2.1.1",
    "toner_atual": "1.3.6.1.2.1.43.11.1.1.9.1.1",
    "toner_full": "1.3.6.1.2.1.43.11.1.1.8.1.1"
}

hp = {
    "contador": "1.3.6.1.2.1.43.10.2.1.4.1.1",
    "tempo_ligada": "1.3.6.1.2.1.1.3.0",
    "N_S": "1.3.6.1.2.1.43.5.1.1.17.1",
    "menssagem_painel": "1.3.6.1.2.1.43.16.5.1.2.1.1",
    "toner_atual": "1.3.6.1.2.1.43.11.1.1.9.1.1",
    "toner_full": "1.3.6.1.2.1.43.11.1.1.8.1.1"
}

epson_color = {
    "contador": "1.3.6.1.2.1.43.10.2.1.4.1.1",
    "tempo_ligada": "1.3.6.1.2.1.1.3.0",
    "N_S": "1.3.6.1.2.1.43.5.1.1.17.1",
    "menssagem_painel": "1.3.6.1.2.1.43.16.5.1.2.1.1",
    "toner_atual_bk": "1.3.6.1.2.1.43.11.1.1.9.1.1",
    "toner_full_bk": "1.3.6.1.2.1.43.11.1.1.8.1.1",
    "toner_atual_c": "1.3.6.1.2.1.43.11.1.1.9.1.2",
    "toner_full_c": "1.3.6.1.2.1.43.11.1.1.8.1.2",
    "toner_atual_m": "1.3.6.1.2.1.43.11.1.1.9.1.3",
    "toner_full_m": "1.3.6.1.2.1.43.11.1.1.8.1.3",
    "toner_atual_y": "1.3.6.1.2.1.43.11.1.1.9.1.4",
    "toner_full_y": "1.3.6.1.2.1.43.11.1.1.8.1.4",
    "caixa_manutenção_atual": "1.3.6.1.2.1.43.11.1.1.9.1.5",
    "caixa_manutenção_full": "1.3.6.1.2.1.43.11.1.1.8.1.5"
}

SUPPORTED_VENDORS = {
    "Canon": canon,
    "Ricoh": richo,
    "HP": hp,
    "Epson Color": epson_color
}
