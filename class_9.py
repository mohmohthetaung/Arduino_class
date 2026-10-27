"""DHT22 (AM2302) experiment -- Slides 18 to 23 in one Python file.

Requires the Slide 17 Arduino sketch sending: humidity;temperature;heat_index
Install: python -m pip install pyserial matplotlib
Change PORT to your Arduino COM port before running.
"""

# Slide 18: Import the library for serial communication
import serial
import csv
import datetime

# Slides 20-22: Import the library for real-time visualization
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the Arduino board location (change COM3 if necessary)
PORT = "COM3"
uno_board = serial.Serial(PORT, timeout=0, baudrate=9600)

# Slide 19: Initiate figure and axes for humidity
fig_hum, ax_hum = plt.subplots()
x_hum, y_hum = [], []
(line_hum,) = ax_hum.plot([], [])
x_iter_hum = 1
ax_hum.set_title("Real Time Humidity")
ax_hum.set_xlabel("Data Points")
ax_hum.set_ylabel("Humidity (%)")

# Slide 20: Initiate figure and axes for temperature
fig_temp, ax_temp = plt.subplots()
x_temp, y_temp = [], []
(line_temp,) = ax_temp.plot([], [])
x_iter_temp = 1
ax_temp.set_title("Real Time Temperature")
ax_temp.set_xlabel("Data Points")
ax_temp.set_ylabel("Temperature (C)")

# Slide 21: Initiate figure and axes for heat index
fig_hi, ax_hi = plt.subplots()
x_hi, y_hi = [], []
(line_hi,) = ax_hi.plot([], [])
x_iter_hi = 1
ax_hi.set_title("Real Time Heat Index")
ax_hi.set_xlabel("Data Points")
ax_hi.set_ylabel("Heat Index (C)")


def init_hum():
    # Set initial parameters for the plot
    ax_hum.set_xlim(0, 100)
    ax_hum.set_ylim(0, 100)
    return (line_hum,)


def animate_hum(data_plot):
    global x_iter_hum

    # Append data to x and y data lists
    x_hum.append(x_iter_hum)
    y_hum.append(data_plot)

    # Adjust limit after 100 points
    limit = max(100, max(x_hum))
    ax_hum.set_xlim(limit - 100, limit)

    # Set data for line plot
    line_hum.set_data(x_hum, y_hum)
    x_iter_hum += 1
    return (line_hum,)


def init_temp():
    # Set initial parameters for the plot
    ax_temp.set_xlim(0, 100)
    ax_temp.set_ylim(0, 100)
    return (line_temp,)


def animate_temp(data_plot):
    global x_iter_temp

    # Append data to x and y data lists
    x_temp.append(x_iter_temp)
    y_temp.append(data_plot)

    # Adjust limit after 100 points
    limit = max(100, max(x_temp))
    ax_temp.set_xlim(limit - 100, limit)

    # Set data for line plot
    line_temp.set_data(x_temp, y_temp)
    x_iter_temp += 1
    return (line_temp,)


def init_hi():
    # Set initial parameters for the plot
    ax_hi.set_xlim(0, 100)
    ax_hi.set_ylim(0, 100)
    return (line_hi,)


def animate_hi(data_plot):
    global x_iter_hi

    # Append data to x and y data lists
    x_hi.append(x_iter_hi)
    y_hi.append(data_plot)

    # Adjust limit after 100 points
    limit = max(100, max(x_hi))
    ax_hi.set_xlim(limit - 100, limit)

    # Set data for line plot
    line_hi.set_data(x_hi, y_hi)
    x_iter_hi += 1
    return (line_hi,)


# Slide 18: Save each measurement to a CSV file
def save_measurements(timestamp, humidity, temperature, heat_index):
    with open("humidity_history.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, humidity])

    with open("temperature_history.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, temperature])

    with open("heat_index_history.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, heat_index])


# Slides 18-19 and 23: Read Arduino values and update the three plots
incoming = bytearray()


def init_all():
    init_hum()
    init_temp()
    init_hi()
    return (line_hum,)


def update_from_arduino(_frame):
    global incoming

    # Accumulate serial bytes until a complete line is available
    try:
        count = uno_board.in_waiting
        if count:
            incoming.extend(uno_board.read(count))
    except serial.SerialException as error:
        print("Serial error:", error)
        return (line_hum,)

    new_data = False
    while b"\n" in incoming:
        raw_line, _, remaining = incoming.partition(b"\n")
        incoming = bytearray(remaining)
        data = raw_line.decode("utf-8", errors="replace").strip()

        # Arduino Slide 17 sends: humidity;temperature;heat_index
        parts = data.split(";")
        if len(parts) != 3:
            continue
        try:
            humidity, temperature, heat_index = [float(p) for p in parts]
        except ValueError:
            continue

        timestamp = datetime.datetime.now()
        save_measurements(timestamp, humidity, temperature, heat_index)

        animate_hum(humidity)
        animate_temp(temperature)
        animate_hi(heat_index)
        new_data = True

        print(
            f"Humidity: {humidity:.2f}% | "
            f"Temperature: {temperature:.2f} C | "
            f"Heat Index: {heat_index:.2f} C"
        )

    if new_data:
        # Animation redraws fig_hum; redraw the other two figures, too
        fig_temp.canvas.draw_idle()
        fig_hi.canvas.draw_idle()
    return (line_hum,)


# Slide 23: Plot the measurements in their respective figures
print("Reading DHT22 on", PORT, "(9600 baud). Close Arduino Serial Monitor.")
ani_hum = FuncAnimation(
    fig_hum,
    update_from_arduino,
    init_func=init_all,
    interval=500,
    cache_frame_data=False,
)

try:
    plt.show()
finally:
    uno_board.close()
