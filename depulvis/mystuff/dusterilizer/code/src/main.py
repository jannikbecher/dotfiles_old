import uasyncio as asyncio
from uasyncio.queues import Queue
from machine import I2C, Pin
import network
import utime
import ntptime

from math import ceil
import ujson

from tasks.display_task import *
from tasks.mqtt_task import *
from tasks.sps30_task import *
from tasks.sht31_task import *
from tasks.logic_task import *

def init_dip_button():
    btn = [None] * 8
    btn_list = [36, 39, 34, 35, 32, 33, 15, 16]
    # declare all dip pins as input
    for i in range(0, 8):
        btn[i] = Pin(btn_list[i], Pin.IN, Pin.PULL_UP)

    # read values
    res = ''
    for i in range(0, 8):
        res += str(btn[i].value())

    # pull all pins low
    for i in range(4, 8):
        pin = Pin(btn_list[i], Pin.OUT)
        pin.value(0)

    return int(res, 2)

def init_i2c():
    scl_pin = Pin(4, Pin.OUT)
    sda_pin = Pin(5, Pin.OUT)
    i2c = I2C(scl=scl_pin, sda=sda_pin, freq=100000)
    return i2c

def init_lan():
    lan = network.LAN(mdc=Pin(23), mdio=Pin(18), phy_type=network.PHY_LAN8720, phy_addr=1)
    try:
        lan.active(1)
    except:
        print("Couldn't initialize LAN")
    return lan

def init_fan():
    pin = Pin(32, Pin.OUT)
    pin.value(1)

async def main_task(loop):

    # initialize features
    connect() # TOOD: write seperate function for wlan
    ntptime.settime() # set time
    #config_num = init_dip_button()
    config_num = 5
    i2c = init_i2c()
    lan = init_lan()
    init_fan()

    print(config_num)

    # configs
    display_config = {
        'pin_r': 16,
        'pin_l': 17,
        'num_leds': 14,
        'update_rate': 1.5
    }
    sps30_config = {
        'i2c': i2c,
        'lock': None,
        'update_rate': 1.5
    }
    sht31_config = {
        'i2c': i2c,
        'lock': None,
        'update_rate': 1.5
    }
    logic_config = {
        'logic_pin': 33
    }
    mqtt_config = {
        'broker': '192.168.50.100'
    }

    f = open('config.json', 'r')
    configs = ujson.load(f)["config"]
    f.close()

    mode = configs[config_num]["mode"]
    thres = configs[config_num]["thres"]

    # initialize queues
    main_queue = Queue()
    display_queue = Queue()
    mqtt_queue = Queue()
    logic_queue = Queue()

    # initialize tasks
    display_instance = display_task(display_queue, display_config)
    mqtt_instance = mqtt_task(mqtt_queue, mqtt_config)
    sps30_instance = sps30_task(main_queue, sps30_config)
    sht31_instance = sht31_task(main_queue, sht31_config)
    logic_instance = logic_task(logic_queue, logic_config)

    # starting tasks
    loop.create_task(display_instance)
    loop.create_task(mqtt_instance)
    loop.create_task(sps30_instance)
    loop.create_task(sht31_instance)
    loop.create_task(logic_instance)

    print("Config: " + str(config_num))
    await display_queue.put(('percent', config_num/8)) # TODO: change config_num
    time.sleep(2)

    pm10_percent = 0
    co2_percent = 0
    voc_percent = 0

    while True:
        msg = await main_queue.get()
        data = msg[1]
        if msg[0] == 'sps30_info':
            #print(data)
            pass
        elif msg[0] == 'sps30_data':
            pm10_percent = data["pm10_mass"] / thres["pm10"]
            print("PM10: " + str(data["pm10_mass"]))
            await mqtt_queue.put(('pm', data))
        elif msg[0] == 'sht31_info':
            print(data)
        elif msg[0] == 'sht31_data':
            print(data)
        else:
            print('unkown message: ' + msg[0])

        display_percent = max(pm10_percent, co2_percent, voc_percent)
        if display_percent >= 1.0:
            await logic_queue.put(('on', ''))
        else:
            await logic_queue.put(('off', ''))
        await display_queue.put(('percent_smooth', display_percent))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main_task(loop))
    loop.run_forever()
