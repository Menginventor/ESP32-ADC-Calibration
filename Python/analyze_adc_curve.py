import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import os

# === Locate Latest NPZ in /data/ ===
data_dir = os.path.join(os.path.dirname(__file__), 'data')
files = sorted(glob(os.path.join(data_dir, "esp32_dac_adc_corrected_*.npz")))
if not files:
    raise FileNotFoundError("No data file found. Run data collection first.")
latest_file = files[-1]
print(f"📂 Loading: {latest_file}")

# === Load Data ===
data = np.load(latest_file)
dac_raw = data['dac']
adc_raw = data['adc_raw']
adc_corrected = data['adc_corrected']

# === Convert to Voltage ===
v_ref = 3.3
dac_voltage = dac_raw * (v_ref / 255.0)
adc_raw_voltage = adc_raw * (v_ref / 4095.0)
adc_corrected_voltage = adc_corrected * (v_ref / 4095.0)

# === Average ADC voltage per DAC step ===
unique_dac = np.unique(dac_raw)
avg_raw = []
avg_corr = []
avg_dac_v = []

for val in unique_dac:
    indices = np.where(dac_raw == val)
    avg_dac_v.append(val * v_ref / 255.0)
    avg_raw.append(np.mean(adc_raw_voltage[indices]))
    avg_corr.append(np.mean(adc_corrected_voltage[indices]))

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(dac_voltage, adc_raw_voltage, '.', alpha=0.2, label="Raw ADC")
plt.plot(dac_voltage, adc_corrected_voltage, '.', alpha=0.2, label="Corrected ADC")
plt.plot(avg_raw, avg_dac_v, 'b-', label="Avg Raw ADC → DAC")
plt.plot(avg_corr, avg_dac_v, 'g-', label="Avg Corrected ADC → DAC")
plt.plot([0, v_ref], [0, v_ref], 'k--', label="Unity line (y = x)")
plt.xlabel("ADC Input Voltage (V)")
plt.ylabel("DAC Output Voltage (V)")
plt.title("Averaged ADC Response per DAC Step")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
