import uasyncio as asyncio
from umqtt.simple import MQTTClient
import machine
import ubinascii
import struct
import ujson
import utime

async def mqtt_task(mqtt_queue, config):
    broker = config['broker']

    client_id = b'esp32_' + ubinascii.hexlify(machine.unique_id())
    client = MQTTClient(client_id, broker)
    client.connect()

    try:
        while True:
            msg = await mqtt_queue.get()
            data = msg[1]
            if msg[0] == 'pm':
                data['timestamp'] = utime.time()
                print(ujson.dumps(data))
                client.publish('pm', bytearray(ujson.dumps(data)))
            elif msg[0] == 'hum/tmp':
                client.publish('hum/tmp', bytearray(data))
            else:
                print('unkown message: ' + msg[0])
    except asyncio.CancelledError:
        return
