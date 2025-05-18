import numpy as np
import matplotlib.pyplot as plt
import serial
from datetime import datetime
import  os
# === Configuration ===
SERIAL_PORT = 'COM3'             # ← Change to your actual ESP32 port
BAUD_RATE = 115200
TRIGGER_CHAR = 'S'
DAC_LEVELS = 256
SAMPLES_PER_LEVEL = 100
TOTAL_LINES = DAC_LEVELS * SAMPLES_PER_LEVEL

# === Serial Setup ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
input("🔁 Press Enter to start data acquisition...")
ser.reset_input_buffer()
ser.write(TRIGGER_CHAR.encode('utf-8'))

# === Data Containers ===
dac_vals = []
adc_raw_vals = []
adc_corrected_vals = []

print("📡 Receiving data...")

progress_checkpoint = 0

while len(dac_vals) < TOTAL_LINES:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            parts = line.split('\t')
            if len(parts) == 3:
                dac, raw_adc, corrected_adc = map(int, parts)
                dac_vals.append(dac)
                adc_raw_vals.append(raw_adc)
                adc_corrected_vals.append(corrected_adc)

                # Progress update
                progress = len(dac_vals) / TOTAL_LINES
                if progress >= progress_checkpoint / 100:
                    print(f"🔄 Progress: {progress_checkpoint}% ({len(dac_vals)}/{TOTAL_LINES})")
                    progress_checkpoint += 10
    except Exception:
        continue

ser.close()
print(f"✅ Done! Collected {len(dac_vals)} samples.")

# === Convert to Voltages ===
v_ref = 3.3
dac_voltage = np.array(dac_vals) * (v_ref / 255.0)
adc_raw_voltage = np.array(adc_raw_vals) * (v_ref / 4095.0)
adc_corrected_voltage = np.array(adc_corrected_vals) * (v_ref / 4095.0)

# === Save ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(output_dir, exist_ok=True)

# Save file inside /Python/data/
filename = f"esp32_dac_adc_corrected_{timestamp}.npz"
filepath = os.path.join(output_dir, filename)
np.savez(filepath, dac=dac_vals, adc_raw=adc_raw_vals, adc_corrected=adc_corrected_vals)
print(f"💾 Saved: {filepath}")

print(f"💾 Saved: {filename}")

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(dac_voltage, adc_raw_voltage, '.', alpha=0.2, label="Raw ADC")
plt.plot(dac_voltage, adc_corrected_voltage, '.', alpha=0.2, label="Corrected ADC")
plt.plot([0, v_ref], [0, v_ref], 'k--', label="Unity Line (y = x)")
plt.xlabel("DAC Output Voltage (V)")
plt.ylabel("ADC Input Voltage (V)")
plt.title("ESP32 ADC Correction Visualization")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
