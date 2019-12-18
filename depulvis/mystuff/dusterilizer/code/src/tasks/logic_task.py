import uasyncio as asyncio

from machine import Pin

async def logic_task(logic_queue, config):
    pin = Pin(config['logic_pin'], Pin.OUT, Pin.PULL_DOWN)

    try:
        while True:
            msg = await logic_queue.get()
            data = msg[1]
            if msg[0] == 'on':
                pin.on()
            elif msg[0] == 'off':
                pin.off()
            else:
                print('unkown message in logic_task' + msg)
    except asyncio.CancelledError:
        return
