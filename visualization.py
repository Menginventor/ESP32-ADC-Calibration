import numpy as np
import matplotlib.pyplot as plt
from glob import glob

# === Load Latest NPZ File ===
files = sorted(glob("esp32_dac_adc_*.npz"))
if not files:
    raise FileNotFoundError("No data file found. Run the collection script first.")
latest_file = files[-1]
data = np.load(latest_file)
print(data)
dac_raw = data['dac']
adc_raw = data['adc_raw']

# === Convert to Voltage ===
v_ref = 3.3
dac_voltage = dac_raw * (v_ref / 255.0)
adc_voltage = adc_raw * (v_ref / 4095.0)

# === Compute average ADC for each DAC level ===
unique_dac = np.unique(dac_raw)
avg_adc_voltage = []
avg_dac_voltage = []

for val in unique_dac:
    indices = np.where(dac_raw == val)
    avg_adc_voltage.append(np.mean(adc_voltage[indices]))
    avg_dac_voltage.append(val * v_ref / 255.0)

# === Plot ===
plt.figure(figsize=(10, 5))
plt.plot(dac_voltage,adc_voltage, '.', alpha=0.2, label="Raw Measured")
plt.plot(avg_dac_voltage,avg_adc_voltage, 'ro--', linewidth=2, label="Average per DAC Value")
plt.plot([0, v_ref], [0, v_ref], 'k--', label="Unity line (y = x)")


plt.ylabel("ADC Input Voltage (V)")
plt.xlabel("DAC Output Voltage (V)")
plt.title("ESP32 DAC to ADC Voltage Curve (Averaged)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
