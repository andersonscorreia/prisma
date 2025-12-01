import asyncio
from datetime import datetime, timezone, timedelta
from puresnmp import Client, V2C, PyWrapper
from puresnmp.exc import NoSuchOID
from impressoras import *


# =====================================================
# FUNÇÃO SNMP SEGURO
# =====================================================

async def snmp_safe_get(ip, oid, decode=False):
    """
    Tenta pegar um OID. Se der erro, retorna "N/A".
    """
    client = PyWrapper(Client(ip, V2C("public")))
    try:
        value = await client.get(oid)
        if decode and isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        return value
    except NoSuchOID:
        return "N/A"
    except Exception:
        return "N/A"


# =====================================================
# FUNÇÕES ESPECÍFICAS
# =====================================================

async def toner_pb(ip, atual_oid, full_oid):
    atual = await snmp_safe_get(ip, atual_oid)
    full = await snmp_safe_get(ip, full_oid)

    if isinstance(atual, str) or isinstance(full, str):
        return "N/A"

    if full == 0:
        return "N/A"

    return round((atual / full) * 100, 2)


async def toner_colorido(ip, impressora):
    cores = ["bk", "c", "m", "y"]
    resultado = {}

    for cor in cores:
        atual = await snmp_safe_get(ip, impressora[f"toner_atual_{cor}"])
        full = await snmp_safe_get(ip, impressora[f"toner_full_{cor}"])

        if isinstance(atual, str) or isinstance(full, str) or full == 0:
            resultado[cor] = "N/A"
        else:
            resultado[cor] = round((atual / full) * 100, 2)

    # caixa de manutenção
    atual_m = await snmp_safe_get(ip, impressora["caixa_manutenção_atual"])
    full_m = await snmp_safe_get(ip, impressora["caixa_manutenção_full"])

    if isinstance(atual_m, str) or isinstance(full_m, str) or full_m == 0:
        resultado["manutencao"] = "N/A"
    else:
        resultado["manutencao"] = round((atual_m / full_m) * 100, 2)

    return resultado


# =====================================================
# COLETA GERAL
# =====================================================

def coleta_dados(ip, impressora):
    hora_local = datetime.now(timezone.utc) - timedelta(hours=3)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    is_color = "toner_atual_bk" in impressora

    tarefas = [
        snmp_safe_get(ip, impressora["contador"]),
        snmp_safe_get(ip, impressora["tempo_ligada"]),
        snmp_safe_get(ip, impressora["N_S"], decode=True),
        snmp_safe_get(ip, impressora["menssagem_painel"], decode=True)
    ]

    if is_color:
        tarefas.append(toner_colorido(ip, impressora))
    else:
        tarefas.append(toner_pb(ip, impressora["toner_atual"], impressora["toner_full"]))

    contador_val, tempo_val, serial_val, msg_val, toner_val = loop.run_until_complete(asyncio.gather(*tarefas))

    if not is_color:
        toner_val = {"bk": toner_val}

    return {
        "device_ip": ip,
        "timestamp": hora_local.strftime("%d/%m/%Y %H:%M:%S"),
        "contador": contador_val,
        "tempo_ligada": tempo_val,
        "numero_serie": serial_val,
        "mensagem_erro": msg_val,
        "toner": toner_val
    }


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


# =====================================================
# MAIN
# =====================================================

def main():
    ip = input("IP da impressora: ")
    marca = input("1-Canon | 2-Ricoh | 3-Epson Color: ")

    if marca == "1":
        impressora = canon
    elif marca == "2":
        impressora = richo
    elif marca == "3":
        impressora = epson_color
    else:
        print("Opção inválida!")
        return

    dados = coleta_dados(ip, impressora)
    print("\n=== RESULTADO FINAL ===")
    print(dados)


if __name__ == "__main__":
    main()
