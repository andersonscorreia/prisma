import asyncio
import aiosnmp


"""Função para obter apenas o valor do contador de páginas via SNMP."""

async def contador(ip):
    
    oid_contador = '1.3.6.1.2.1.43.10.2.1.4.1.1'

    try:
        async with aiosnmp.Snmp(host=ip, port=161, community='public') as snmp:
            results = await snmp.get(oid_contador)
            for res in results:
                print(f"Contador: {res.value}") 

    except aiosnmp.exceptions.SnmpError as e:
        print(f"Ocorreu um erro SNMP: {e}")


"""Função para obter o nível de toner em porcentagem via SNMP."""
async def toner(ip):
   
    oid_toner_level = '1.3.6.1.2.1.43.11.1.1.9.1.1'  # nível atual
    oid_toner_max = '1.3.6.1.2.1.43.11.1.1.8.1.1'    # capacidade máxima

    try:
        async with aiosnmp.Snmp(host=ip, port=161, community='public') as snmp:
            # Obtém nível atual
            results_level = await snmp.get(oid_toner_level)
            toner_atual = None
            for res in results_level:
                toner_atual = res.value

            # Obtém capacidade máxima
            results_max = await snmp.get(oid_toner_max)
            toner_max = None
            for res in results_max:
                toner_max = res.value

            if toner_atual is not None and toner_max is not None:
                toner_percent = (toner_atual / toner_max) * 100
                print(f"Nível de toner: {toner_percent:.2f}%")
            else:
                print("Não foi possível obter o nível de toner corretamente.")

    except aiosnmp.exceptions.SnmpError as e:
        print(f"Ocorreu um erro SNMP: {e}")


ip='10.19.104.97'

asyncio.run(contador(ip))
asyncio.run(toner(ip))