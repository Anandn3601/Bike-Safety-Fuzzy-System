import pandas as pd
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

mf_params_df = pd.read_csv("output_fuzzy_mf_parameters_safe.csv")

universes = {
    'speed': np.linspace(0, 120, 100),               
    'rpm': np.linspace(1000, 6000, 100),             
    'acceleration': np.linspace(0, 100, 100),        
    'throttle': np.linspace(0, 100, 100),            
    'power': np.linspace(0, 5, 100),                 
    'intake_pressure': np.linspace(15, 100, 100),    
    'lean': np.linspace(0, 70, 100)                  
}

fuzzy_inputs = {}
for var in ['speed', 'rpm', 'acceleration', 'throttle', 'power', 'intake_pressure']:
    fuzzy_inputs[var] = ctrl.Antecedent(universes[var], var)

fuzzy_inputs['lean'] = ctrl.Antecedent(universes['lean'], 'lean')
fuzzy_inputs['lean']['low'] = fuzz.trimf(universes['lean'], [0.0, 0.0, 20.0])
fuzzy_inputs['lean']['medium'] = fuzz.trimf(universes['lean'], [20.0, 25.0, 30.0])
fuzzy_inputs['lean']['high'] = fuzz.trimf(universes['lean'], [30.0, 50.0, 70.0])

for _, row in mf_params_df.iterrows():
    var = row['Variable']
    label = row['Label'].lower()
    a, b, c = row['a'], row['b'], row['c']
    fuzzy_inputs[var][label] = fuzz.trimf(universes[var], [a, b, c])

safety = ctrl.Consequent(np.linspace(0, 10, 100), 'safety')
safety['safe'] = fuzz.trimf(safety.universe, [0, 0, 3])
safety['moderately_safe'] = fuzz.trimf(safety.universe, [2, 4, 6])
safety['unsafe'] = fuzz.trimf(safety.universe, [5, 7, 9])
safety['highly_unsafe'] = fuzz.trimf(safety.universe, [8, 10, 10])

print("Fuzzy input and output variables defined.")

fuzzy_variables = {
    **fuzzy_inputs,
    'safety': safety
}
