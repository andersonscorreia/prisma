import asyncio
from puresnmp import Client, V2C, PyWrapper

async def contador(ip):
   client = PyWrapper(Client(ip, V2C("public")))
   output = await client.get("1.3.6.1.2.1.43.10.2.1.4.1.1")
   return output



ip = '192.168.2.169'

print(asyncio.run(contador(ip)))