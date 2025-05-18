import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from scipy.interpolate import interp1d

# === Load Latest NPZ File ===
files = sorted(glob("esp32_dac_adc_*.npz"))
if not files:
    raise FileNotFoundError("No data file found.")
latest_file = files[-1]
data = np.load(latest_file)

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

avg_adc_voltage = np.array(avg_adc_voltage)
avg_dac_voltage = np.array(avg_dac_voltage)

# === Build inverse: adc_voltage → ideal_dac_voltage
adc_to_dac_interp = interp1d(avg_adc_voltage, avg_dac_voltage,
                             kind='linear', bounds_error=False, fill_value='extrapolate')

# === Generate corrected ADC value from ideal voltage ===
ideal_adc_interp = lambda v: np.clip(np.round((v / v_ref) * 4095), 0, 4095).astype(int)

# === Create the final lookup table ===
adc_raw_values = np.arange(4096)
adc_voltage_values = (adc_raw_values / 4095.0) * v_ref
corrected_voltage = adc_to_dac_interp(adc_voltage_values)
corrected_adc_values = ideal_adc_interp(corrected_voltage)

# === Plot the visual flow ===
plt.figure(figsize=(12, 6))

# Subplot 1: Calibration curve
plt.subplot(1, 2, 1)
plt.plot(dac_voltage, adc_voltage, '.', alpha=0.2, label='Raw Data')
plt.plot(avg_dac_voltage, avg_adc_voltage, 'ro-', label='Avg Points')
plt.xlabel("DAC Output Voltage (V)")
plt.ylabel("ADC Input Voltage (V)")
plt.title("Raw vs Averaged ADC Response")
plt.legend()
plt.grid(True)

# Subplot 2: Lookup Table Mapping
plt.subplot(1, 2, 2)
plt.plot(adc_raw_values, corrected_adc_values, 'b-')
plt.xlabel("Raw ADC Value (0–4095)")
plt.ylabel("Corrected ADC Value")
plt.title("Generated Lookup Table")
plt.grid(True)

plt.tight_layout()
plt.show()

