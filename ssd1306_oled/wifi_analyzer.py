
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

Micropython code to scan for wireless networks and display the top 3 on an OLED display

Author: Lakhya Jyoti Nath
Date: September 2022

"""


from time import sleep

# import ssd1306
from machine import Pin
from network import WLAN, STA_IF
from ssd1306_oled_display import OledDisplayI2C, OledDisplaySPI


class WirelessNetwork:
    """
    WirelessNetwork class for handling all wireless network operation
    """

    def __init__(self) -> None:
        self.__nic = WLAN(STA_IF)
        self.__nic.active(True)                         # activating wireless network adapter

    def scan(self) -> list:
        """
        Method to scan for all available wirelesss SSIDs
        """
        return self.__nic.scan()


def main():
    """
    Driver function
    """

    script_kill_pin = 5
    if Pin(script_kill_pin, Pin.IN).value() == 0:
        raise SystemExit

    i2c_display = OledDisplayI2C(background_color=False, header_lines_to_retain=3)
    i2c_display.init_display(scl=22, sda=21)

    spi_display = OledDisplaySPI(background_color=False, header_lines_to_retain=3)
    spi_display.init_display(dc=4, rst=5, cs=15, sck=14, mosi=13, miso=12)


    i2c_display.show_text('-Wifi Analyzer-')
    i2c_display.show_text('Updating in 5sec')
    i2c_display.show_text('')

    spi_display.show_text('-Wifi Analyzer-')
    spi_display.show_text('Updating in 5sec')
    spi_display.show_text('')

    wifi_network = WirelessNetwork()
    while True:
        results = wifi_network.scan()
        
        for i in range(3):
            i2c_display.show_text(f'{i+1}.{results[i][0].decode("ascii")}')
            spi_display.show_text(f'{i+1}.{results[i][0].decode("ascii")}')

        sleep(5)


if __name__ == '__main__':
    main()
