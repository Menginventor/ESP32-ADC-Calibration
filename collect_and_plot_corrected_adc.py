import numpy as np
import matplotlib.pyplot as plt
import serial
from datetime import datetime

# === Configuration ===
SERIAL_PORT = 'COM3'  # Change this to your ESP32 port
BAUD_RATE = 115200
TRIGGER_CHAR = 'S'
NUM_DAC_VALUES = 256
SAMPLES_PER_DAC = 100
TOTAL_LINES = NUM_DAC_VALUES * SAMPLES_PER_DAC

# === Serial Communication ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
input("✅ Press Enter to start acquisition...")
ser.reset_input_buffer()
ser.write(TRIGGER_CHAR.encode('utf-8'))

# === Data containers ===
dac_vals = []
adc_raw_vals = []
adc_corrected_vals = []

print("📡 Receiving data...")
while len(dac_vals) < TOTAL_LINES:
    try:
        line = ser.readline().decode().strip()
        parts = line.split('\t')
        if len(parts) == 3:
            dac, raw_adc, corrected_adc = map(int, parts)
            dac_vals.append(dac)
            adc_raw_vals.append(raw_adc)
            adc_corrected_vals.append(corrected_adc)
    except Exception:
        continue

ser.close()
print(f"✅ Done! Collected {len(dac_vals)} samples.")

# === Convert to voltage ===
v_ref = 3.3
dac_voltage = np.array(dac_vals) * (v_ref / 255.0)
adc_raw_voltage = np.array(adc_raw_vals) * (v_ref / 4095.0)
adc_corrected_voltage = np.array(adc_corrected_vals) * (v_ref / 4095.0)

# === Save data ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f"esp32_dac_adc_corrected_{timestamp}.npz",
         dac=dac_vals,
         adc_raw=adc_raw_vals,
         adc_corrected=adc_corrected_vals)

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(dac_voltage, adc_raw_voltage, '.', alpha=0.2, label="Raw ADC")
plt.plot(dac_voltage, adc_corrected_voltage, '.', alpha=0.2, label="Corrected ADC")
plt.plot([0, v_ref], [0, v_ref], 'k--', label="Unity line")
plt.xlabel("DAC Output Voltage (V)")
plt.ylabel("ADC Input Voltage (V)")
plt.title("ESP32 ADC Correction Comparison")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
