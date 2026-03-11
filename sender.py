import aiohttp
import asyncio
import logging

API_URL = "http://localhost/printer-api/public/api/printers"
API_STATUS_URL = "http://localhost/printer-api/public/api/status"
API_KEY = "sua_api_key_aqui_se_houver"

async def send_to_api(data: dict) -> bool:
    """

    Envia o dicionário de dados coletados da impressora via POST JSON
    para a API Laravel.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        # "Authorization": f"Bearer {API_KEY}" # Descomente se precisar autenticar
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status in (200, 201):
                    # logging.info(f"Dados enviados com sucesso para {data.get('device_ip', 'IP Desconhecido')}")
                    return True
                else:
                    texto = await response.text()
                    logging.error(f"Erro na API ({response.status}): {texto}")
                    return False
    except asyncio.TimeoutError:
        logging.error(f"Timeout ao tentar enviar dados (IP: {data.get('device_ip')}) para a API.")
        return False
    except Exception as e:
        logging.error(f"Erro de conexão com a API: {e}")
        return False

async def check_sync_status():
    """
    Pergunta à API qual o intervalo configurado e se devemos
    forçar uma coleta agora mesmo.
    Retorno default caso falhe: {"interval": 300, "force_update": False}
    """
    default_status = {"interval": 300, "force_update": False}
    
    headers = {
        "Accept": "application/json",
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_STATUS_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "interval": data.get("interval", 300),
                        "force_update": data.get("force_update", False)
                    }
                else:
                    return default_status
    except Exception as e:
        logging.error(f"Erro ao verificar status da API: {e}")
        return default_status
