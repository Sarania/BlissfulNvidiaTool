"""
=================================================
                  Blissful Nvidia Tool
=================================================
Description:
Simple CLI tool for monitoring and overclocking Nvidia Graphics Cards

Dependencies:
nvidia-ml-py - NOT pynvml which is the older, deprecated version and does not have the needed functionality for all features.
Nvidia Driver 555.xx or greater for all features.

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
__VERSION__ = "1.00"
import argparse
import pynvml as nv
parser = argparse.ArgumentParser(description="Blissful Nvidia Tool")
parser.add_argument("--gpu-number", type=int, default=0, help="Specify the GPU index (default: 0)")
parser.add_argument("--refresh-rate", type=int, default=1000, help="Specify how often to refresh the monitor, in milliseconds. Default is 1000")
parser.add_argument("--set-clocks", nargs=2, type=int, help="Set core and memory clock offsets (in MHz) respectively. Example: --set-clocks -150 500")
parser.add_argument("--set-power-limit", type=int, help="Set the power limit (in watts). Example: --set-power-limit 300")
parser.add_argument("--set-max-fan", action='store_true', help="Set all fans to maximum speed")
parser.add_argument("--set-auto-fan", action='store_true', help="Reset fan control to automatic mode")
parser.add_argument("--set-custom-fan", type=int, help="Set a custom fan percentage. !BE CAREFUL! as this changes the fan control policy to manual!!! Only values 30-100 are accepted. ")
parser.add_argument("--reactive-color", action='store_true', help="Uses color to indicate the intensity of values")


def draw_dashboard(stdscr):
    """
    Main function for drawing monitor, takes in a screen pointer
    """
    def set_color(value, threshold_caution, threshold_warn):
        """
        Helper function to return color values based on current readings, takes in the value and thresholds to check
        """
        if threshold_caution < value < threshold_warn:
            return 4
        elif value > threshold_warn:
            return 2
        else:
            return 1

    def add_sign(offset):
        """
        Helper function to add a + sign to positive numbers and output them back
        """
        return f"+{offset}" if offset > 0 else offset

    stdscr.clear()
    stdscr.nodelay(True)  # Non-blocking input
    curses.curs_set(0)    # Hide cursor
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)
    temp_color = 7
    power_color = 7
    clock_color = 7
    util_color = 7
    vram_color = 7

    while True:
        current_core_offset = nv.nvmlDeviceGetGpcClkVfOffset(gpu)
        current_mem_offset = nv.nvmlDeviceGetMemClkVfOffset(gpu) / 2
        #  If the offset is negative, pynvml may return a value that is munged by truncated overflow
        #  Since offsets will never legitimately be this large, this should be a safe fix.
        if current_core_offset > 100000:
            current_core_offset = current_core_offset - 4294966
        if current_mem_offset > 100000:
            current_mem_offset = current_mem_offset - 4294966
        core_offset_sign = add_sign(current_core_offset)
        mem_offset_sign = add_sign(current_mem_offset)
        gpu_name = nv.nvmlDeviceGetName(gpu)
        fan_speed = nv.nvmlDeviceGetFanSpeed(gpu)
        current_temperature = nv.nvmlDeviceGetTemperature(gpu, 0)
        current_power_usage = nv.nvmlDeviceGetPowerUsage(gpu) / 1000  # Convert mW to W
        utilization = nv.nvmlDeviceGetUtilizationRates(gpu)
        mem_info = nv.nvmlDeviceGetMemoryInfo(gpu)
        core_clock = nv.nvmlDeviceGetClockInfo(gpu, nv.NVML_CLOCK_GRAPHICS)
        core_clock_str = f"{core_clock} Mhz core ({core_offset_sign} Mhz)" if current_core_offset != 0 else f"{core_clock} Mhz core"
        max_core_clock = nv.nvmlDeviceGetMaxClockInfo(gpu, nv.NVML_CLOCK_GRAPHICS)
        mem_clock = nv.nvmlDeviceGetClockInfo(gpu, nv.NVML_CLOCK_MEM)
        mem_clock_str = f"{mem_clock} Mhz mem ({mem_offset_sign} Mhz)" if current_mem_offset != 0 else f"{mem_clock} Mhz mem"
        current_power_limit = nv.nvmlDeviceGetPowerManagementLimit(gpu) / 1000
        default_power_limit = nv.nvmlDeviceGetPowerManagementDefaultLimit(gpu) / 1000
        current_power_offset = current_power_limit - default_power_limit
        power_offset_str = add_sign(current_power_offset)
        current_power_percentage = (current_power_usage / current_power_limit) * 100
        current_clock_percentage = (core_clock / max_core_clock) * 100
        current_vram_percentage = (mem_info.used / mem_info.total) * 100
        if args.reactive_color:
            temp_color = set_color(current_temperature, 65, 80)
            power_color = set_color(current_power_percentage, 70, 90)
            clock_color = set_color(current_clock_percentage, 70, 90)
            util_color = set_color(utilization.gpu, 70, 90)
            vram_color = set_color(current_vram_percentage, 70, 90)

        stdscr.addstr(3, 0, "GPU: ")
        stdscr.addstr(4, 0, "Clock Frequency: ")
        stdscr.addstr(5, 0, "Temp: ")
        stdscr.addstr(6, 0, "Power: ")
        stdscr.addstr(7, 0, "Utilization: ")
        stdscr.addstr(8, 0, "VRAM Usage: ")
        stdscr.addstr(0, 0, "                    Blissful Nvidia Tool", curses.color_pair(5))
        stdscr.addstr(1, 0, "------------------------------------------------------------")
        stdscr.addstr(3, 18, f"{args.gpu_number} - {gpu_name}", curses.color_pair(1))
        stdscr.addstr(4, 18, f"{core_clock_str} / {mem_clock_str}", curses.color_pair(clock_color))
        stdscr.addstr(5, 18, f"{current_temperature}°C / Fan: {fan_speed}%", curses.color_pair(temp_color))
        stdscr.addstr(6, 18, f"{current_power_usage:.2f} / {current_power_limit:.2f} W ({power_offset_str} W)", curses.color_pair(power_color))
        stdscr.addstr(7, 18, f"Core: {utilization.gpu}% / Memory Controller: {utilization.memory}%", curses.color_pair(util_color))
        stdscr.addstr(8, 18, f"{mem_info.used / (1024**2):.2f} / {mem_info.total / (1024**2):.2f} MB", curses.color_pair(vram_color))

        stdscr.refresh()
        stdscr.timeout(args.refresh_rate)
        key = stdscr.getch()
        if key == ord('q'):
            break
        stdscr.clear()


# Execution begins here
args = parser.parse_args()
nv.nvmlInit()
gpu = nv.nvmlDeviceGetHandleByIndex(args.gpu_number)

if args.set_clocks or args.set_power_limit or args.set_max_fan or args.set_auto_fan or args.set_custom_fan:
    print("Blissful Nvidia Tool Non-interactive Mode")
    print("_________________________________________")
    print("User accepts ALL risks of overclocking/altering power limits/fan settings!")
    print("Additionally, root permission is needed for these changes and the script will fail without it!")
    print()
    print("Enabling persistence...")
    print()
    nv.nvmlDeviceSetPersistenceMode(gpu, 1)
    if args.set_max_fan:
        num_fans = nv.nvmlDeviceGetNumFans(gpu)
        print(f"Found {num_fans} fans!")
        print("Attempting to set fans to max speed...")
        for i in range(0, num_fans):
            nv.nvmlDeviceSetFanControlPolicy(gpu, i, nv.NVML_FAN_POLICY_MANUAL)
            nv.nvmlDeviceSetFanSpeed_v2(gpu, i, 100)
        print("Fans set to max speed!")
        print()
    elif args.set_auto_fan:
        num_fans = nv.nvmlDeviceGetNumFans(gpu)
        print(f"Found {num_fans} fans!")
        print("Attempting to restore fans to automatic control...")
        for i in range(0, num_fans):
            nv.nvmlDeviceSetFanControlPolicy(gpu, i, nv.NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW)
            nv.nvmlDeviceSetDefaultFanSpeed_v2(gpu, i)
        print("Fans restored to automatic control!")
        print()
    elif args.set_custom_fan:
        new_speed = args.set_custom_fan
        if 101 > new_speed > 29:
            num_fans = nv.nvmlDeviceGetNumFans(gpu)
            print(f"Found {num_fans} fans!")
            print(f"Attempting to set fans to {new_speed}%...")
            for i in range(0, num_fans):
                nv.nvmlDeviceSetFanControlPolicy(gpu, i, nv.NVML_FAN_POLICY_MANUAL)
                nv.nvmlDeviceSetFanSpeed_v2(gpu, i, new_speed)
            print(f"Fans set to {new_speed}%! Please monitor your temps as fan control policy is now MANUAL!")
            print()
        elif new_speed > 100:
            print(f"Value {new_speed} invalid for fan control!")
        else:
            print("Refusing to set fans below 30%! Sorry!")
            print()
    if args.set_clocks:
        core_offset, mem_offset = args.set_clocks
        print(f"Attempting to set core clock offset to {core_offset} MHz and memory clock offset to {mem_offset} MHz...")
        nv.nvmlDeviceSetGpcClkVfOffset(gpu, core_offset)
        nv.nvmlDeviceSetMemClkVfOffset(gpu, mem_offset * 2)  # Multiply memoffset by 2 so it's equivalent to offset in GWE and Windows
        print(f"Set core clock offset to {core_offset} MHz and memory clock offset to {mem_offset} MHz!")
        print()
    if args.set_power_limit:
        print(f"Attempting to set power limit to {args.set_power_limit} W...")
        nv.nvmlDeviceSetPowerManagementLimit(gpu, args.set_power_limit * 1000)
        print(f"Power limit set to {args.set_power_limit} W!")
        print()
else:
    import curses
    curses.wrapper(draw_dashboard)
nv.nvmlShutdown()
