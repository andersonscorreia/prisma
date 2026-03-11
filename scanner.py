import asyncio
import socket
from puresnmp import Client, V2C, PyWrapper

# OID para pegar a descrição do sistema do dispositivo SNMP.
SYS_DESC_OID = "1.3.6.1.2.1.1.1.0"
# OID base para o contador total de páginas em impressoras
PRINTER_COUNTER_OID = "1.3.6.1.2.1.43.10.2.1.4.1.1"

# Palavras-chave conhecidas que costumam aparecer em nomes e descrições de impressoras
PRINTER_KEYWORDS = ["canon", "ricoh", "epson", "hp", "brother", "lexmark", "samsung", "laserjet"]

async def check_ip(ip: str, semaphore: asyncio.Semaphore) -> dict | None:
    async with semaphore:
        client = PyWrapper(Client(ip, V2C("public")))
        try:
            # 1. Traz a descrição do sistema (temos de assegurar que responde algo)
            value = await asyncio.wait_for(client.get(SYS_DESC_OID), timeout=1.0)
            
            if isinstance(value, bytes):
                sys_desc = value.decode("utf-8", errors="ignore")
            else:
                sys_desc = str(value)
                
            # 2. Testa leitura na árvore exclusiva de impressoras (.43)
            # Se a leitura falhar (NoSuchOID), cairá no except abaixo e verificaremos pelo nome.
            try:
                await asyncio.wait_for(client.get(PRINTER_COUNTER_OID), timeout=1.0)
                is_printer_by_oid = True
            except Exception:
                is_printer_by_oid = False

            # 3. Lógica de Validação: Tem o contador OR tem o nome da marca
            sys_desc_lower = sys_desc.lower()
            is_printer_by_name = any(word in sys_desc_lower for word in PRINTER_KEYWORDS)
            
            if is_printer_by_oid or is_printer_by_name:
                print(f"[IMPRESSORA ENCONTRADA] IP: {ip} - Desc: {sys_desc.strip()}")
                return {"ip": ip, "sys_desc": sys_desc}
                
            # Respondeu SNMP, mas não parece uma impressora (ex. Switch)
            return None
            
        except Exception:
            # Host offline ou sem SNMP
            return None

def get_local_network_prefix() -> str:
    """
    Descobre o IP local da interface ativa utilizando uma conexão UDP simulada.
    Essa abordagem não envia dados, mas interroga a tabela de roteamento do SO
    para achar o IP da interface padrão (Wi-Fi/Ethernet) prioritária.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não é necessário alcançar a internet. Apenas força a resolução de rota.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        # Fallback local
        ip = socket.gethostbyname(socket.gethostname())
    finally:
        s.close()
        
    partes = str(ip).split(".")
    if len(partes) >= 3:
        return f"{partes[0]}.{partes[1]}.{partes[2]}"
    return "192.168.1"


async def scan_network(network_prefix: str) -> list[dict]:
    """
    Varre os hosts de 1 a 254 dentro de um sufixo de rede (/24).
    Retorna a lista de dispositivos que responderam.
    """
    # Controle de concorrência: 50 requests assíncronos snmp simultâneos
    semaphore = asyncio.Semaphore(50)
    
    print(f"\n[SCANNER] Iniciando varredura na rede {network_prefix}.X ...")
    
    tarefas = []
    # Cria tarefas para todos os hosts válidos na sub-rede /24
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        tarefas.append(check_ip(ip, semaphore))
        
    # Executa as 254 tarefas. O semaphore vai lidar com o throughput máximo.
    resultados = await asyncio.gather(*tarefas)
    
    # Filtra None e agrupa numa lista final
    encontradas = [r for r in resultados if r is not None]
    
    print(f"[SCANNER] Varredura finalizada. Encontrados {len(encontradas)} dispositivos com SNMP.")
    return encontradas
