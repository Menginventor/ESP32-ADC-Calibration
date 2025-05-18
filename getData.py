import serial
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# === Configuration ===
SERIAL_PORT = 'COM3'  # Change to your actual port (e.g., /dev/ttyUSB0 or COM3)
BAUD_RATE = 115200
TRIGGER_CHAR = 'S'
MAX_LINES = 256 * 100  # 256 DAC steps * 10 samples per step

# === Start Serial Communication ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
input("Press Enter to start data collection...")

# Flush and trigger
ser.reset_input_buffer()
ser.write(TRIGGER_CHAR.encode('utf-8'))

# === Read and store data ===
dac_vals = []
adc_vals = []

print("Receiving data...")
while len(dac_vals) < MAX_LINES:
    try:
        line = ser.readline().decode().strip()
        if '\t' in line:
            dac_str, adc_str = line.split('\t')
            dac_vals.append(int(dac_str))
            adc_vals.append(int(adc_str))
    except ValueError:
        continue

ser.close()
print(f"Finished receiving {len(dac_vals)} samples.")

# === Convert to numpy and save ===
dac_vals = np.array(dac_vals)
adc_vals = np.array(adc_vals)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f"esp32_dac_adc_{timestamp}.npz", dac=dac_vals, adc=adc_vals)

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(dac_vals, adc_vals, '.', alpha=0.5)
plt.xlabel("DAC Value (0–255)")
plt.ylabel("ADC Reading (0–4095)")
plt.title("ESP32 DAC Output vs ADC33 Input")
plt.grid(True)
plt.tight_layout()
plt.show()
