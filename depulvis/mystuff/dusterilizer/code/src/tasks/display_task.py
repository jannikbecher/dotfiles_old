from display import Display
import uasyncio as asyncio
import time

from math import ceil

async def display_task(display_queue, config):
    num_leds = config['num_leds']
    led_display = Display(config['pin_l'], config['pin_r'], num_leds)
    update_rate = config['update_rate']

    last_msg = None
    last_percent = 0.0

    pulse_rate = 60

    try:
        while True:
            msg = await display_queue.get()
            if msg != last_msg:
                last_msg = msg
                data = msg[1]
                if msg[0] == 'percent_smooth':
                    if data >= 1.0:
                        for i in range(pulse_rate/2):
                            led_display.display_pulse((-0.8/(pulse_rate/2))*i+1)
                            time.sleep(update_rate/pulse_rate)
                        await asyncio.sleep(0)
                        for i in range(pulse_rate/2):
                            led_display.display_pulse((0.8/(pulse_rate/2))*i+0.2)
                            time.sleep(update_rate/pulse_rate)
                        await asyncio.sleep(0)
                    else:
                        percent = data
                        num_prev_leds = ceil(last_percent*num_leds)
                        num_active_leds = ceil(percent*num_leds)
                        leds_to_update = abs(num_prev_leds-num_active_leds)
                        if leds_to_update > 0:
                            if percent > last_percent:
                                for i in range(num_prev_leds, num_active_leds):
                                    led_display.display_values(i/num_leds)
                                    await asyncio.sleep(update_rate/leds_to_update)
                            else:
                                for i in range(num_prev_leds-1, num_active_leds-1, -1):
                                    led_display.display_values(i/num_leds)
                                    await asyncio.sleep(update_rate/leds_to_update)
                    last_percent = data
                elif msg[0] == 'percent':
                    led_display.display_config(data)
                else:
                    print('unkown message in display task ' + str(msg))
    except asyncio.CancelledError:
        return
