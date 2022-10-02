
"""
MIT License

Copyright (c) 2022 ljnath

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Micropython code to connect to show current time.
To get the latest time, it connects to wireless network and gets time from NTP server

Author: Lakhya Jyoti Nath
Date: September 2022

"""


from time import sleep

import ntptime
import utime
from machine import RTC, Pin
from network import STA_IF, WLAN

from ssd1306_oled_display import OledDisplaySPI

SSID_TO_CONNECT = 'Guest_2.4GHz'
SSID_KEY = 'guest-pass'

ASIA_TIMEZONE_DIFF_IN_SEC = 19800

display = OledDisplaySPI(background_color=False, header_lines_to_retain=3)
display.init_display(dc=4, rst=5, cs=15, sck=14, mosi=13, miso=12)

months = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec',
}


def connect_to_network() -> str:
    """
    Function to connect to wireless network
    :return ip_address
    """
    nic = WLAN(STA_IF)
    nic.active(True)

    while nic.isconnected() is False:
        # connecting to wireless network if not connected
        display.show_text('Searching...')
        results = nic.scan()

        avilable_ssids = [_item[0].decode('ascii') for _item in results]
        if SSID_TO_CONNECT in avilable_ssids:
            display.show_text('SSID found!')
            display.show_text('Connecting...')
            nic.connect(SSID_TO_CONNECT, SSID_KEY)
        else:
            display.show_text('SSID missing :(')

        sleep(3)

    display.show_text('Connected!')
    sleep(2)
    network_ips = nic.ifconfig()
    display.show_text(f'IP: {network_ips[0]}')

    return network_ips[0]


def update_time():
    """
    Function to update RTC via NTP
    """
    rtc = RTC()
    current_time = rtc.datetime()
    display.show_text(f'RTC:{months.get(current_time[1])} {current_time[2]:02d},{current_time[0]}')
    display.show_text(f'RTC:{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d} Hrs.')

    display.show_text('Updt time...')
    ntptime.settime()
    sleep(2)


def show_clock(ip: str = None):
    """
    Method to show the clodk
    """
    while True:
        current_time = utime.localtime(utime.time() + ASIA_TIMEZONE_DIFF_IN_SEC)
        display.clear()
        display.show_text('  ESP Clock 0.1')

        display.show_text(f'Date:{months.get(current_time[1])} {current_time[2]:02d},{current_time[0]}', y=20)
        display.show_text(f'Time:{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}Hrs.', y=30)

        if ip:
            display.show_text(f'IP: {ip}', y=50)

        sleep(1)


def main():
    """
    Driver function
    """

    # # DEBUGGING
    script_kill_pin = 5
    if Pin(script_kill_pin, Pin.IN).value() == 0:
        raise SystemExit

    display.show_text('  ESP Clock 0.1')
    display.show_text('')

    ip_address = connect_to_network()
    update_time()
    show_clock(ip=ip_address)


if __name__ == '__main__':
    main()
