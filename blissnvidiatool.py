"""
=================================================
                  Blissful Nvidia CLI Tool
=================================================
Description:
Simple CLI tool for monitoring and overclocking Nvidia Graphics Cards

Dependencies:
nvidia-ml-py - NOT pynvml which is the older, deprecated version and does not have the needed functionality.
Nvidia Driver 555.xx or greater

License:
MIT License - See below for full text

=================================================
Copyright (c) 2024 Blyss Sarania

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

=================================================
Created on: Tue Oct 1, 2024
@author: Blyss Sarania
=================================================
"""

import curses
import argparse
import time
from pynvml import *
parser = argparse.ArgumentParser(description="Blissful Nvidia Tool")
parser.add_argument("--gpu-number", type=int, default=0, help="Specify the GPU index (default: 0)")
parser.add_argument("--set-clocks", nargs=2, type=int, help="Set core and memory clock offsets (in MHz) respectively. Example: --set-clocks -150 500")
parser.add_argument("--set-power-limit", type=int, help="Set the power limit (in watts). Example: --set-power-limit 300")
parser.add_argument("--set-max-fan", action='store_true', help="Set fan to maximum speed")
parser.add_argument("--set-auto-fan", action='store_true', help="Reset fan control to automatic mode")


def set_clock_offset(gpu, core_offset, mem_offset):
    nvmlDeviceSetGpcClkVfOffset(gpu, core_offset)
    nvmlDeviceSetMemClkVfOffset(gpu, mem_offset)


def draw_dashboard(stdscr):
    stdscr.clear()
    stdscr.nodelay(True)  # Non-blocking input
    curses.curs_set(0)    # Hide cursor

    while True:
        # Read metrics
        gpu_name = nvmlDeviceGetName(gpu)
        fan_speed = nvmlDeviceGetFanSpeed(gpu)
        temperature = nvmlDeviceGetTemperature(gpu, 0)
        current_power_usage = nvmlDeviceGetPowerUsage(gpu) / 1000  # Convert mW to W
        utilization = nvmlDeviceGetUtilizationRates(gpu)
        mem_info = nvmlDeviceGetMemoryInfo(gpu)
        core_clock = nvmlDeviceGetClockInfo(gpu, NVML_CLOCK_GRAPHICS)
        mem_clock = nvmlDeviceGetClockInfo(gpu, NVML_CLOCK_MEM)
        current_power_limit = nvmlDeviceGetPowerManagementLimit(gpu) / 1000
        default_power_limit = nvmlDeviceGetPowerManagementDefaultLimit(gpu) / 1000

        # Display metrics
        stdscr.addstr(0, 0, "Blissful Nvidia CLI Tool")
        stdscr.addstr(1, 0, "--------------------")
        stdscr.addstr(3, 0, f"GPU: {args.gpu_number} - {gpu_name} ")
        stdscr.addstr(4, 0, f"Current Clock frequency: {core_clock}Mhz core / {mem_clock}Mhz mem")
        stdscr.addstr(5, 0, f"Temp: {temperature}°C Fan: {fan_speed}%")
        stdscr.addstr(6, 0, f"Power: {current_power_usage} / {current_power_limit} W ({default_power_limit}W)")
        stdscr.addstr(7, 0, f"GPU Utilization: {utilization.gpu}%")
        stdscr.addstr(8, 0, f"Memory Utilization: {utilization.memory}%")
        stdscr.addstr(9, 0, f"Memory Info: {mem_info.used / (1024**2)} MB / {mem_info.total / (1024**2)} MB")

        # Refresh the display
        stdscr.refresh()

        # Check for exit condition
        key = stdscr.getch()
        if key == ord('q'):
            break
        time.sleep(1)
        stdscr.clear()


args = parser.parse_args()
nvmlInit()
gpu = nvmlDeviceGetHandleByIndex(args.gpu_number)

if args.set_clocks or args.set_power_limit or args.set_max_fan or args.set_auto_fan:
    print("Blissful Nvidia CLI Tool Non-interactive Mode")
    print("_________________________________________")
    print("User accepts ALL risks of overclocking/altering power limits!")
    print("Additionally, root permission is needed for these changes and the script will fail without it!")
    print()
    print("Enabling persistence...")
    print()
    nvmlDeviceSetPersistenceMode(gpu, 1)
    if args.set_max_fan:
        num_fans = nvmlDeviceGetNumFans(gpu)
        print(f"Found {num_fans} fans!")
        print("Attempting to set fans to max speed...")
        for i in range(0, num_fans):
            nvmlDeviceSetFanSpeed_v2(gpu, i, 100)
        print("Fans set to max speed!")
        print()
    if args.set_auto_fan:
        num_fans = nvmlDeviceGetNumFans(gpu)
        print(f"Found {num_fans} fans!")
        print("Attempting to restore fans to automatic control...")
        for i in range(0, num_fans):
            nvmlDeviceSetDefaultFanSpeed_v2(gpu, i)
        print("Fans restored to automatic control!")
        print()
    if args.set_clocks:
        core_offset, mem_offset = args.set_clocks
        print(f"Attempting to set core clock offset to {core_offset} MHz and memory clock offset to {mem_offset} MHz...")
        set_clock_offset(gpu, core_offset, mem_offset * 2)  # Multiply memoffset by 2 so it's equivalent to offset in GWE and Windows
        print(f"Set core clock offset to {core_offset} MHz and memory clock offset to {mem_offset} MHz!")
        print()
    if args.set_power_limit:
        print(f"Attempting to set power limit to {args.set_power_limit} W...")
        nvmlDeviceSetPowerManagementLimit(gpu, args.set_power_limit * 1000)
        print(f"Power limit set to {args.set_power_limit} W!")
        print()
else:
    curses.wrapper(draw_dashboard)
