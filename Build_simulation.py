import pandas as pd
import numpy as np
import math
from skfuzzy import control as ctrl
from define_fuzzy_variables import fuzzy_variables
from define_fuzzy_rules import rules

obd_df = pd.read_csv("safe_riding.csv")
sensor_df = pd.read_csv("20250601_142500_imu.csv")

sensor_df["lean"] = np.degrees(np.arctan2(sensor_df["accel_x"], sensor_df["accel_z"])).abs()

min_len = min(len(obd_df), len(sensor_df))
obd_df = obd_df.iloc[:min_len].reset_index(drop=True)
sensor_df = sensor_df.iloc[:min_len].reset_index(drop=True)
obd_df["lean"] = sensor_df["lean"]

df = obd_df[['Vehicle speed (km/h)', 'Engine RPM (rpm)', 'Calculated engine load value (%)',
             'Relative throttle position (%)', 'Instant engine power (based on fuel consumption) (hp)',
             'Intake manifold absolute pressure (psi)', 'lean']].copy()

speed = fuzzy_variables['speed']
rpm = fuzzy_variables['rpm']
acceleration = fuzzy_variables['acceleration']
throttle = fuzzy_variables['throttle']
power = fuzzy_variables['power']
intake_pressure = fuzzy_variables['intake_pressure']
lean = fuzzy_variables['lean']
safety = fuzzy_variables['safety']
system = ctrl.ControlSystem(rules)

scores = []
labels = []

for i, row in df.iterrows():
    try:
        sim = ctrl.ControlSystemSimulation(system)
        sim.input['speed'] = row['Vehicle speed (km/h)']
        sim.input['rpm'] = row['Engine RPM (rpm)']
        sim.input['acceleration'] = row['Calculated engine load value (%)']
        sim.input['throttle'] = row['Relative throttle position (%)']
        sim.input['power'] = row['Instant engine power (based on fuel consumption) (hp)']
        sim.input['intake_pressure'] = row['Intake manifold absolute pressure (psi)']
        sim.input['lean'] = row['lean']
        sim.compute()

        score = round(sim.output['safety'])
        scores.append(score)

        if score <= 3:
            label = "Safe"
        elif score <= 5:
            label = "Moderately Safe"
        elif score <= 7:
            label = "Unsafe"
        else:
            label = "Highly Unsafe"
        labels.append(label)

    except Exception as e:
        scores.append(None)
        labels.append("No Result")

df['Safety Score'] = scores
df['Safety Label'] = labels
df.to_csv("Result/fuzzy_results_real_lean_safe.csv", index=False)

valid_scores = [s for s in scores if s is not None]
mean_score = round(np.mean(valid_scores), 2)
percent_unsafe = 100 * sum(l in ["Unsafe", "Highly Unsafe"] for l in labels) / len(labels)

print("Fuzzy safety simulation complete.")
print(f"- Mean Safety Score: {mean_score}")
print(f"- Session Rating: {'Safe' if mean_score <= 3 else 'Moderately Safe' if mean_score <= 5 else 'Unsafe' if mean_score <= 7 else 'Highly Unsafe'}")
print(f"- {percent_unsafe:.1f}% of entries marked Unsafe or Highly Unsafe.")
print("Results saved to: fuzzy_results_real_lean.csv")
