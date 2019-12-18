from sgp30 import SGP30
import uasyncio as asyncio

async def sgp30_task(main_queue, config):
    sgp30 = SGP30(config['i2c'])
    lock = config['lock']
    update_rate = config['update_rate']

    if sgp30.init():
        await main_queue.put(('sgp30_info', 'ok'))
    else:
        await main_queue.put(('sgp30_info', 'error'))
        return

    try:
        while True:
            sgp30.measure_air_quality()
            if sgp30.status[0] == 'error':
                print(sgp30.status[1])
                await main_queue.put(('sgp30_info', 'error'))
            else:
                # TODO: create communication protocol (not substracting 400 from co2)
                await main_queue.put(('sgp30_data', {"co2": sgp30.eco2-400, "voc": sgp30.tvoc}))
            await asyncio.sleep(update_rate)
    except asyncio.CancelledError:
        return
