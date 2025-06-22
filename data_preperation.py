import pandas as pd
import os

INPUT_FILE = "safe_riding.csv"
assert os.path.exists(INPUT_FILE), f"Input file {INPUT_FILE} not found."

bike_df = pd.read_csv(INPUT_FILE)

selected_vars = {
    'Vehicle speed (km/h)': 'speed',
    'Engine RPM (rpm)': 'rpm',
    'Calculated engine load value (%)': 'acceleration',
    'Relative throttle position (%)': 'throttle',
    'Instant engine power (based on fuel consumption) (hp)': 'power',
    'Intake manifold absolute pressure (psi)': 'intake_pressure'
}

stats = bike_df[list(selected_vars.keys())].describe(percentiles=[.25, .5, .75])
stats = stats.loc[['min', '25%', '50%', '75%', 'max']]
stats.index = ['min', 'q1', 'median', 'q3', 'max']

mf_params = []
for col, short_name in selected_vars.items():
    minv = stats.loc['min', col]
    q1 = stats.loc['q1', col]
    median = stats.loc['median', col]
    q3 = stats.loc['q3', col]
    maxv = stats.loc['max', col]
    mf_params += [
        {'Variable': short_name, 'Label': 'Low',    'a': minv,   'b': minv,   'c': q1},
        {'Variable': short_name, 'Label': 'Medium', 'a': q1,     'b': median, 'c': q3},
        {'Variable': short_name, 'Label': 'High',   'a': median, 'b': maxv,   'c': maxv}
    ]

stats.to_csv("output_descriptive_stats_safe.csv")
pd.DataFrame(mf_params).to_csv("output_fuzzy_mf_parameters_safe.csv", index=False)

print("Data preparation complete. Files saved:")
print("- output_descriptive_stats.csv")
print("- output_fuzzy_mf_parameters.csv")
