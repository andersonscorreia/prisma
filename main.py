import asyncio
from vendors import canon, richo, epson_color
from collector import coleta_dados
from sender import envia_api
from scanner import scan_network, get_local_network_prefix

async def processa_impressora(ip, impressora):
    """
    Orquestra a coleta de SNMP e o envio de HTTP de uma única impressora de forma assíncrona.
    """
    print(f"\n[INFO] Iniciando coleta para o IP: {ip}")
    dados = await coleta_dados(ip, impressora)
    
    print("\n=== RESULTADO DA COLETA ===")
    print(dados)
    
    print(f"\n[INFO] Enviando dados do IP {ip} para a API...")
    sucesso = await envia_api(dados)
    
    if sucesso:
        print(f"[SUCESSO] Processo concluído para {ip}.")
    else:
        print(f"[FALHA] Não foi possível concluir o envio de dados para {ip}.")

async def modo_automatico(prefixo: str, impressora_padrao: dict):
    """
    Varre a rede e, para todas as impressoras encontradas, tenta extrair os dados e enviar para a API.
    (Na prática, você precisaria identificar autonomamente a marca de acordo com o SysDesc,
    neste exemplo estamos usando uma marca _default_ apenas por fins didáticos)
    """
    dispositivos = await scan_network(prefixo)
    
    if not dispositivos:
        print("[AVISO] Nenhuma impressora encontrada nesta rede.")
        return
        
    print("\n[MODO AUTO] Iniciando coletas massivas...")
    # Roda as tarefas de coleta para todo o grid encontrado.
    # Note que se demorar muito, você também pode usar semaphore aqui,
    # Mas como varremos uma subrede local estática, o overhead de processamento de dezenas é baixo.
    tarefas = [processa_impressora(d["ip"], impressora_padrao) for d in dispositivos]
    await asyncio.gather(*tarefas)
    print("\n[MODO AUTO] Todas as operações de rede finalizadas.")

async def main():
    """
    Menu Principal do Sistema
    """
    print("====================================")
    print("      MONITORAMENTO DE IMPRESSÃO      ")
    print("====================================")
    print("[1] Escanear Rede (Mapeamento)")
    print("[2] Monitoramento Manual (1 IP)")
    print("[3] Modo Automático (Varredura > API)")
    print("====================================")
    
    opcao = input("Selecione a opção: ")
    
    if opcao == "1":
        prefixo = get_local_network_prefix()
        print(f"\n[INFO] Detectando rede local: {prefixo}.X...")
        dispositivos = await scan_network(prefixo)
        
        print("\n=== IMPRESSORAS IDENTIFICADAS ===")
        for d in dispositivos:
            print(f"- IP: {d['ip']} | Modelo/SisDesc: {d['sys_desc']}")
            
    elif opcao == "2":
        ip = input("\nIP da impressora: ")
        marca = input("1-Canon | 2-Ricoh | 3-Epson Color: ")

        if marca == "1":
            impressora = canon
        elif marca == "2":
            impressora = richo
        elif marca == "3":
            impressora = epson_color
        else:
            print("Opção de impressora inválida!")
            return

        # Inicia o fluxo para a porta individual
        await processa_impressora(ip, impressora)
        
    elif opcao == "3":
        prefixo = get_local_network_prefix()
        print(f"\n[INFO] Detectando rede local: {prefixo}.X...")
        marca = input("\nQual dicionário de marca utilizar em massa? (1-Canon | 2-Ricoh | 3-Epson): ")
        
        if marca == "1":
            impressora = canon
        elif marca == "2":
            impressora = richo
        elif marca == "3":
            impressora = epson_color
        else:
            print("Opção de impressora inválida!")
            return
            
        await modo_automatico(prefixo, impressora)
        
    else:
        print("Opção inválida.")
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado no sistema: {e}")
