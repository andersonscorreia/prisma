import asyncio
import requests
from datetime import datetime, timezone, timedelta
from puresnmp import Client, V2C, PyWrapper

from impressoras import *

'''
API_URL = "https://seu-servidor.com/api/impressoras"  # troque para sua API
API_KEY = "SUA_API_KEY_AQUI"

'''


async def contador(ip, oid):
    client = PyWrapper(Client(ip, V2C("public")))
    output = await client.get(oid)
    return output

async def toner_pb(ip, toner_atual, toner_full):
    client = PyWrapper(Client(ip, V2C("public")))
    output1 = await client.get(toner_atual)
    output2 = await client.get(toner_full)
    return (output1 / output2) * 100

async def tempo_ligada(ip, oid):
    client = PyWrapper(Client(ip, V2C("public")))
    output = await client.get(oid)
    return output

async def N_S(ip, oid):
    client = PyWrapper(Client(ip, V2C("public")))
    output = await client.get(oid)
    return output.decode("utf-8")

async def menssagem_painel(ip, oid):
    client = PyWrapper(Client(ip, V2C("public")))
    output = await client.get(oid)
    return output.decode("utf-8")

# ---------- Coleta todos os dados em paralelo ---------- #
def coleta_dados(ip, impressora):
    hora_local = datetime.now(timezone.utc) - timedelta(hours=3) 
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tasks = [
        contador(ip, impressora["contador"]),
        toner_pb(ip, impressora["toner_atual"], impressora["toner_full"]),
        tempo_ligada(ip, impressora["tempo_ligada"]),
        N_S(ip, impressora["N_S"]),
        menssagem_painel(ip, impressora["menssagem_painel"])
    ]

    resultado = loop.run_until_complete(asyncio.gather(*tasks))
    contador_val, toner_val, tempo_val, serial_val, mensagem_val = resultado

    dados = {
        "device_ip": ip,
        "timestamp_coleta": hora_local.strftime("%d/%m/%Y %H:%M:%S"),
        "contador": int(contador_val),
        "nivel_toner": round(toner_val, 2),
        "tempo_ligada": str(tempo_val),
        "mensagem_erro": mensagem_val,
        "numero_serie": serial_val
    }

    return dados
'''
# ---------- Envia JSON via requests ---------- #
def envia_api(dados, retries=3):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    for tentativa in range(retries):
        try:
            resp = requests.post(API_URL, json=dados, headers=headers, timeout=10)
            resp.raise_for_status()
            print(f"[OK] Dados enviados para {dados['device_ip']}")
            return True
        except Exception as e:
            print(f"[ERRO] Tentativa {tentativa+1} falhou: {e}")
    print(f"[FALHA] Não foi possível enviar dados para {dados['device_ip']}")
    return False
'''
# ---------- Main ---------- #
def main():
   ip = input("- Qual o IP da impressora: ")
   marca = input("- Qual a marca da impressora - \n1 - canon\n2 - richo\n3 - epson\n")

   if marca == "1":
      impressora = canon
   elif marca == "2":
      impressora = richo
   elif marca == "3":
      impressora = epson
   else:
      raise ValueError("Marca inválida")

   dados = coleta_dados(ip, impressora)
    #envia_api(dados)
   print(dados)  
if __name__ == "__main__":
    main()
