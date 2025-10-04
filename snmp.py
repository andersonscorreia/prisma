import asyncio
import aiosnmp

async def main():
    """Função principal para demonstrar o uso do aiosnmp."""
    try:
        async with aiosnmp.Snmp(
            host='10.19.104.97', # Substitua pelo endereço IP do seu dispositivo
            port=161,
            community='public'
        ) as snmp:
            # Obtém a descrição do sistema (sysDescr)
            results = await snmp.get('1.3.6.1.2.1.43.10.2.1.4.1.1')
            for res in results:
                print(f"OID: {res.oid}, Valor: {res.value}")

    except aiosnmp.exceptions.SnmpError as e:
        print(f"Ocorreu um erro SNMP: {e}")

if __name__ == "__main__":
    asyncio.run(main())
