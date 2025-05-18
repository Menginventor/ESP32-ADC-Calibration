import numpy as np
from glob import glob
from scipy.interpolate import interp1d
import os

# === Load Latest NPZ ===
data_dir = os.path.join(os.path.dirname(__file__), 'data')
files = sorted(glob(os.path.join(data_dir, "esp32_dac_adc_corrected_*.npz")))
if not files:
    raise FileNotFoundError("No data file found. Run data collection first.")
latest_file = files[-1]
print(f"📂 Loading: {latest_file}")

# === Load data ===
data = np.load(latest_file)
dac_raw = data['dac']
adc_raw = data['adc_raw']

# === Convert to Voltage ===
v_ref = 3.3
dac_voltage = dac_raw * (v_ref / 255.0)
adc_voltage = adc_raw * (v_ref / 4095.0)

# === Average ADC voltage per DAC level ===
unique_dac = np.unique(dac_raw)
avg_adc_voltage = []
avg_dac_voltage = []

for val in unique_dac:
    indices = np.where(dac_raw == val)
    avg_adc_voltage.append(np.mean(adc_voltage[indices]))
    avg_dac_voltage.append(val * v_ref / 255.0)

avg_adc_voltage = np.array(avg_adc_voltage)
avg_dac_voltage = np.array(avg_dac_voltage)

# === Build inverse: adc_voltage → ideal dac voltage
adc_to_dac_interp = interp1d(avg_adc_voltage, avg_dac_voltage,
                             kind='linear', bounds_error=False, fill_value='extrapolate')

# === Convert back to 12-bit corrected ADC value
def voltage_to_adc(v):
    return np.clip(np.round((v / v_ref) * 4095), 0, 4095).astype(int)

adc_raw_values = np.arange(4096)
adc_voltage_values = (adc_raw_values / 4095.0) * v_ref
corrected_voltage = adc_to_dac_interp(adc_voltage_values)
corrected_adc_values = voltage_to_adc(corrected_voltage)

# Optional: Clamp very low values (e.g., raw 0–5) to zero
corrected_adc_values[:5] = 0

# === Generate C header
output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(output_dir, exist_ok=True)
header_path = os.path.join(output_dir, 'adc_correction_lookup.h')

header_lines = [
    "#ifndef ADC_CORRECTION_LOOKUP_H",
    "#define ADC_CORRECTION_LOOKUP_H",
    "",
    "#output <stdint.h>",
    "",
    "const uint16_t adc_correction_lut[4096] = {"
]

body_lines = []
for i in range(0, 4096, 8):
    line = ", ".join(f"{v:4d}" for v in corrected_adc_values[i:i+8])
    body_lines.append("  " + line + ",")

footer_lines = [
    "};",
    "",
    "#endif // ADC_CORRECTION_LOOKUP_H"
]

# === Save to file
with open(header_path, 'w') as f:
    f.write("\n".join(header_lines + body_lines + footer_lines))

print(f"✅ LUT saved to: {header_path}")
