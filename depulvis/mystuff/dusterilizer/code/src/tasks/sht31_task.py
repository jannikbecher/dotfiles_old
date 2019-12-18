from sht31 import SHT31
import uasyncio as asyncio

async def sht31_task(main_queue, config):
    sht31 = SHT31(config['i2c'])
    lock = config['lock']
    update_rate = config['update_rate']

    if sht31.init():
        await main_queue.put(('sht31_info', 'ok'))
    else:
        await main_queue.put(('sht31_info', 'error'))
        return

    try:
        while True:
            sht31.read_measured_values()
            if sht31.status[0] == 'error':
                print(sht31.status[1])
                await main_queue.put(('sht31_info', 'error'))
            else:
                await main_queue.put(('sht31_data', sht31.humidity))
                await main_queue.put(('sht31_data', sht31.temperature))
            await asyncio.sleep(update_rate)
    except asyncio.CancelledError:
        return
