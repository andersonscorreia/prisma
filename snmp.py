import asyncio
from puresnmp import Client, V2C, PyWrapper

richo = {'contador':'1.3.6.1.2.1.43.10.2.1.4.1.1',
         'toner_atual':'1.3.6.1.2.1.43.11.1.1.9.1.1',
         'toner_full':'1.3.6.1.2.1.43.11.1.1.8.1.1',
         'tempo_ligada':'1.3.6.1.2.1.1.3.0',
         'N_S':'1.3.6.1.2.1.43.5.1.1.17.1',
         'menssagem_painel':'1.3.6.1.2.1.43.18.1.1.8.1.1'}


canon= {
    'contador': '1.3.6.1.2.1.43.10.2.1.4.1.1',
    'toner_atual': '1.3.6.1.2.1.43.11.1.1.9.1.1',
    'toner_full': '1.3.6.1.2.1.43.11.1.1.8.1.1',
    'tempo_ligada': '1.3.6.1.2.1.1.3.0',
    'N_S': '1.3.6.1.2.1.43.5.1.1.17.1',
    'menssagem_painel': '1.3.6.1.2.1.43.16.5.1.2.1.1'
}


async def contador(ip,oid):
   client = PyWrapper(Client(ip, V2C('public')))
   output = await client.get(oid)
   return output

async def toner_pb(ip,toner_atual,toner_full):
   client = PyWrapper(Client(ip, V2C('public')))    
   output1 = await client.get(toner_atual)
   output2 = await client.get(toner_full)
   toner_percent = (output1 / output2) * 100
   return toner_percent

async def tempo_ligada(ip,tempo_ligada):
   client = PyWrapper(Client(ip, V2C('public')))
   output = await client.get(tempo_ligada)
   return output
 
async def N_S(ip,N_S):
   client = PyWrapper(Client(ip, V2C('public')))
   output = await client.get(N_S)
   output = output.decode('utf-8')
   return output

async def menssagem_painel(ip,menssagem_painel):
   client = PyWrapper(Client(ip, V2C('public')))
   output = await client.get(menssagem_painel)
   output = output.decode('utf-8')
   return output


ip = '192.168.2.86'


print(asyncio.run(contador(ip,richo['contador'])))

print(asyncio.run(toner_pb(ip,richo['toner_atual'],richo['toner_full'])))

print(asyncio.run(tempo_ligada(ip,richo['tempo_ligada'])))

print(asyncio.run(menssagem_painel(ip,richo['menssagem_painel'])))

print(asyncio.run(N_S(ip,richo['N_S'])))