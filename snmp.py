import asyncio
from puresnmp import Client, V2C, PyWrapper

from impressoras import *

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


ip = input('- Qual o ip da impressora: -\n ')

impressora = input('- qual a marca da impressora - \n1 - canon \n2 - richo\n')


print(asyncio.run(contador(ip,richo['contador'])))

print(asyncio.run(toner_pb(ip,richo['toner_atual'],richo['toner_full'])))

print(asyncio.run(tempo_ligada(ip,richo['tempo_ligada'])))

print(asyncio.run(menssagem_painel(ip,richo['menssagem_painel'])))

print(asyncio.run(N_S(ip,richo['N_S'])))