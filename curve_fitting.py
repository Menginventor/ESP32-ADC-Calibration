import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from scipy.optimize import curve_fit

# === Load Latest NPZ File ===
files = sorted(glob("esp32_dac_adc_*.npz"))
if not files:
    raise FileNotFoundError("No data file found. Run the collection script first.")
latest_file = files[-1]
data = np.load(latest_file)

dac_raw = data['dac']
adc_raw = data['adc']

# === Convert to Voltage ===
v_ref = 3.3
dac_voltage = dac_raw * (v_ref / 255.0)
adc_voltage = adc_raw * (v_ref / 4095.0)

# === Polynomial model functions ===
def poly2(x, a, b, c):
    return a * x**2 + b * x + c

def poly3(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

def poly4(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

def poly5(x, a, b, c, d, e, f):
    return a * x**5 + b * x**4 + c * x**3 + d * x**2 + e * x + f

# === Fit each polynomial ===
params_p2, _ = curve_fit(poly2, dac_voltage, adc_voltage)
params_p3, _ = curve_fit(poly3, dac_voltage, adc_voltage)
params_p4, _ = curve_fit(poly4, dac_voltage, adc_voltage)
params_p5, _ = curve_fit(poly5, dac_voltage, adc_voltage)

# === Predict ===
adc_pred_p2 = poly2(dac_voltage, *params_p2)
adc_pred_p3 = poly3(dac_voltage, *params_p3)
adc_pred_p4 = poly4(dac_voltage, *params_p4)
adc_pred_p5 = poly5(dac_voltage, *params_p5)

# === Compute SSE ===
sse_p2 = np.sum((adc_voltage - adc_pred_p2) ** 2)
sse_p3 = np.sum((adc_voltage - adc_pred_p3) ** 2)
sse_p4 = np.sum((adc_voltage - adc_pred_p4) ** 2)
sse_p5 = np.sum((adc_voltage - adc_pred_p5) ** 2)

# === Plot ===
plt.figure(figsize=(10, 6))
plt.plot(dac_voltage, adc_voltage, '.', alpha=0.3, label="Measured")
plt.plot(dac_voltage, adc_pred_p2, 'g-', label="2nd Order Fit")
plt.plot(dac_voltage, adc_pred_p3, 'r-', label="3rd Order Fit")
plt.plot(dac_voltage, adc_pred_p4, 'b-', label="4th Order Fit")
plt.plot(dac_voltage, adc_pred_p5, 'm-', label="5th Order Fit")
plt.plot([0, v_ref], [0, v_ref], 'k--', label="Unity line")

plt.xlabel("DAC Output Voltage (V)")
plt.ylabel("ADC Input Voltage (V)")
plt.title("Polynomial Fits for ESP32 ADC Non-Linearity")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === Print SSEs and coefficients ===
print("2nd Order SSE:", sse_p2)
print("3rd Order SSE:", sse_p3)
print("4th Order SSE:", sse_p4)
print("5th Order SSE:", sse_p5)
