from skfuzzy import control as ctrl
from define_fuzzy_variables import fuzzy_variables

speed = fuzzy_variables['speed']
rpm = fuzzy_variables['rpm']
acceleration = fuzzy_variables['acceleration']
throttle = fuzzy_variables['throttle']
power = fuzzy_variables['power']
intake_pressure = fuzzy_variables['intake_pressure']
lean = fuzzy_variables['lean']

safety = fuzzy_variables['safety']

rules = [

    # SPEED-LEAN RULES
    ctrl.Rule(speed['high'] & lean['high'], safety['unsafe']),
    ctrl.Rule(speed['medium'] & lean['medium'], safety['moderately_safe']),
    ctrl.Rule(speed['low'] & lean['low'], safety['safe']),
    ctrl.Rule(speed['high'] & lean['medium'], safety['unsafe']),
    ctrl.Rule(speed['low'] & lean['high'], safety['unsafe']),

    # RPM-based 
    ctrl.Rule(rpm['high'] & throttle['high'], safety['highly_unsafe']),
    ctrl.Rule(rpm['medium'] & acceleration['medium'], safety['moderately_safe']),
    ctrl.Rule(rpm['low'] & throttle['low'], safety['safe']),
    ctrl.Rule(rpm['high'] & lean['high'], safety['highly_unsafe']),
    ctrl.Rule(rpm['medium'] & lean['medium'], safety['moderately_safe']),
    ctrl.Rule(rpm['low'] & lean['low'], safety['safe']),

    # THROTTLE and ACCELERATION
    ctrl.Rule(throttle['high'] & acceleration['high'], safety['highly_unsafe']),
    ctrl.Rule(throttle['medium'] & acceleration['medium'], safety['moderately_safe']),
    ctrl.Rule(throttle['low'] & acceleration['low'], safety['safe']),
    ctrl.Rule(throttle['high'] & lean['medium'], safety['unsafe']),
    ctrl.Rule(throttle['low'] & lean['low'], safety['safe']),

    # POWER and RPM
    ctrl.Rule(power['high'] & rpm['high'], safety['highly_unsafe']),
    ctrl.Rule(power['medium'] & rpm['medium'], safety['moderately_safe']),
    ctrl.Rule(power['low'] & rpm['low'], safety['safe']),

    # SPEED and THROTTLE
    ctrl.Rule(speed['high'] & throttle['low'], safety['moderately_safe']),
    ctrl.Rule(speed['medium'] & throttle['medium'], safety['moderately_safe']),
    ctrl.Rule(speed['low'] & throttle['high'], safety['unsafe']),

    # POWER + LEAN
    ctrl.Rule(power['high'] & lean['high'], safety['highly_unsafe']),
    ctrl.Rule(power['medium'] & lean['medium'], safety['unsafe']),
    ctrl.Rule(power['low'] & lean['low'], safety['safe']),

    # COMPOSITE
    ctrl.Rule(speed['high'] & acceleration['high'] & lean['high'], safety['highly_unsafe']),
    ctrl.Rule(speed['low'] & rpm['low'] & lean['low'], safety['safe']),
    ctrl.Rule(speed['medium'] & throttle['high'] & lean['medium'], safety['unsafe']),
    ctrl.Rule(rpm['medium'] & acceleration['high'] & intake_pressure['high'], safety['unsafe']),
    ctrl.Rule(throttle['medium'] & power['medium'] & lean['medium'], safety['moderately_safe']),
    ctrl.Rule(speed['high'] & power['high'] & lean['high'], safety['highly_unsafe']),

    # INTAKE PRESSURE effects
    ctrl.Rule(intake_pressure['high'] & speed['high'], safety['highly_unsafe']),
    ctrl.Rule(intake_pressure['medium'] & rpm['medium'], safety['moderately_safe']),
    ctrl.Rule(intake_pressure['low'] & rpm['low'], safety['safe']),

    # Mixed Conditions
    ctrl.Rule(lean['high'] & acceleration['high'], safety['highly_unsafe']),
    ctrl.Rule(lean['low'] & power['low'] & speed['low'], safety['safe']),
    ctrl.Rule(throttle['medium'] & lean['medium'] & intake_pressure['medium'], safety['moderately_safe']),
    ctrl.Rule(power['high'] & throttle['high'] & rpm['high'], safety['highly_unsafe']),
    ctrl.Rule(power['low'] & intake_pressure['low'] & acceleration['low'], safety['safe']),
    ctrl.Rule(speed['medium'] & acceleration['medium'] & lean['medium'], safety['moderately_safe']),
    ctrl.Rule(speed['low'] & lean['medium'] & throttle['medium'], safety['safe']),
    ctrl.Rule(speed['high'] & lean['medium'] & acceleration['medium'], safety['unsafe']),
    ctrl.Rule(throttle['low'] & lean['high'] & power['medium'], safety['unsafe']),
]

print(f" Defined {len(rules)} fuzzy rules.")
