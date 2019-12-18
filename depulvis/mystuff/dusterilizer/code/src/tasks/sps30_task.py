from sps30 import SPS30
import uasyncio as asyncio

async def sps30_task(main_queue, config):
    sps30 = SPS30(config['i2c'])
    lock = config['lock']
    update_rate = config['update_rate']

    if sps30.init():
        await main_queue.put(('sps30_info', 'ok'))
    else:
        await main_queue.put(('sps30_info', 'error'))
        #return

    try:
        while True:
            sps30.read_measured_values()
            if sps30.status[0] == 'error':
                print(sps30.status[1])
                await main_queue.put(('sps30_info', 'error'))
            else:
                await main_queue.put(('sps30_data', sps30.pm_data))
            await asyncio.sleep(update_rate)
    except asyncio.CancelledError:
        return
