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

Micropython code to display text on a 128x68 OLED display over I2C

Author: Lakhya Jyoti Nath
Date: September 2022

"""


from time import localtime, sleep

from ssd1306_oled_display import OledDisplayI2C


def main():
    """
    Driver function
    """
    oled_display = OledDisplayI2C(background_color=True)
    oled_display.init_display(scl=22, sda=21)

    # for i in range(80):
    #     oled_display.show_text(f'Hello world {i}')
    # return

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

    while True:
        current_time = localtime()
        oled_display.clear()
        oled_display.show_text('ESP Clock 0.1', x=10, y=5)
        oled_display.show_text(f'Date:{months.get(current_time[1])} {current_time[2]},{current_time[0]}', y=25)
        oled_display.show_text(f'Time:{current_time[3]}:{current_time[4]}:{current_time[5]} Hrs.', y=35)

        sleep(1)


if __name__ == '__main__':
    main()
