import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# =========================================================
# 1. FUZZY INPUTS
# =========================================================

budget_match = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'budget_match'
)

camera_match = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'camera_match'
)

gaming_match = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'gaming_match'
)

battery_match = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'battery_match'
)

performance_match = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'performance_match'
)


# =========================================================
# 2. FUZZY OUTPUT
# =========================================================

suitability = ctrl.Consequent(
    np.arange(0, 101, 1),
    'suitability'
)


# =========================================================
# 3. INPUT MEMBERSHIP FUNCTIONS
# =========================================================

for feature in [
    budget_match,
    camera_match,
    gaming_match,
    battery_match,
    performance_match
]:

    feature['low'] = fuzz.trimf(
        feature.universe,
        [0, 0, 45]
    )

    feature['medium'] = fuzz.trimf(
        feature.universe,
        [30, 55, 75]
    )

    feature['high'] = fuzz.trimf(
        feature.universe,
        [60, 85, 100]
    )


# =========================================================
# 4. OUTPUT MEMBERSHIP FUNCTIONS
# =========================================================

suitability['poor'] = fuzz.trimf(
    suitability.universe,
    [0, 0, 30]
)

suitability['below_average'] = fuzz.trimf(
    suitability.universe,
    [20, 35, 50]
)

suitability['average'] = fuzz.trimf(
    suitability.universe,
    [40, 52, 64]
)

suitability['good'] = fuzz.trimf(
    suitability.universe,
    [55, 68, 80]
)

suitability['very_good'] = fuzz.trimf(
    suitability.universe,
    [70, 82, 92]
)

suitability['excellent'] = fuzz.trimf(
    suitability.universe,
    [85, 100, 100]
)


# =========================================================
# 5. FUZZY RULES
# =========================================================

rule1 = ctrl.Rule(
    budget_match['high'] &
    camera_match['high'] &
    gaming_match['high'] &
    battery_match['high'] &
    performance_match['high'],
    suitability['excellent']
)


rule2 = ctrl.Rule(
    budget_match['high'] &
    camera_match['high'] &
    gaming_match['high'] &
    performance_match['high'],
    suitability['very_good']
)


rule3 = ctrl.Rule(
    budget_match['high'] &
    camera_match['high'] &
    battery_match['high'] &
    performance_match['high'],
    suitability['very_good']
)


rule4 = ctrl.Rule(
    budget_match['high'] &
    gaming_match['high'] &
    battery_match['high'] &
    performance_match['high'],
    suitability['very_good']
)


rule5 = ctrl.Rule(
    budget_match['high'] &
    camera_match['high'] &
    performance_match['high'],
    suitability['good']
)


rule6 = ctrl.Rule(
    budget_match['high'] &
    gaming_match['high'] &
    performance_match['high'],
    suitability['good']
)


rule7 = ctrl.Rule(
    budget_match['high'] &
    battery_match['high'] &
    performance_match['high'],
    suitability['good']
)


rule8 = ctrl.Rule(
    camera_match['high'] &
    gaming_match['high'] &
    performance_match['high'],
    suitability['good']
)


rule9 = ctrl.Rule(
    budget_match['medium'] &
    camera_match['high'] &
    gaming_match['high'] &
    performance_match['high'],
    suitability['very_good']
)


rule10 = ctrl.Rule(
    budget_match['medium'] &
    camera_match['high'] &
    battery_match['high'] &
    performance_match['high'],
    suitability['good']
)


rule11 = ctrl.Rule(
    budget_match['medium'] &
    gaming_match['high'] &
    battery_match['high'] &
    performance_match['high'],
    suitability['good']
)


rule12 = ctrl.Rule(
    budget_match['high'] &
    camera_match['medium'] &
    gaming_match['medium'] &
    battery_match['medium'] &
    performance_match['high'],
    suitability['good']
)


rule13 = ctrl.Rule(
    budget_match['high'] &
    camera_match['medium'] &
    gaming_match['high'] &
    battery_match['high'] &
    performance_match['medium'],
    suitability['good']
)


rule14 = ctrl.Rule(
    budget_match['medium'] &
    camera_match['medium'] &
    gaming_match['medium'] &
    battery_match['medium'] &
    performance_match['medium'],
    suitability['average']
)


rule15 = ctrl.Rule(
    camera_match['medium'] &
    gaming_match['medium'] &
    battery_match['medium'],
    suitability['average']
)


rule16 = ctrl.Rule(
    budget_match['low'] &
    camera_match['medium'] &
    gaming_match['medium'],
    suitability['below_average']
)


rule17 = ctrl.Rule(
    budget_match['low'] &
    camera_match['low'] &
    gaming_match['low'],
    suitability['poor']
)


rule18 = ctrl.Rule(
    camera_match['low'] &
    gaming_match['low'] &
    performance_match['low'],
    suitability['poor']
)


# =========================================================
# 6. CONTROL SYSTEM
# =========================================================

phone_control = ctrl.ControlSystem([
    rule1,
    rule2,
    rule3,
    rule4,
    rule5,
    rule6,
    rule7,
    rule8,
    rule9,
    rule10,
    rule11,
    rule12,
    rule13,
    rule14,
    rule15,
    rule16,
    rule17,
    rule18
])


# =========================================================
# 7. USER PREFERENCE → TARGET VALUE
# =========================================================

def get_target_value(preference):

    preference = str(preference).lower().strip()

    if preference == "low":
        return 30

    elif preference == "medium":
        return 60

    elif preference == "high":
        return 85

    return 60


# =========================================================
# 8. CALCULATE FEATURE MATCH
# =========================================================

def calculate_match(phone_value, user_preference):

    target = get_target_value(user_preference)

    try:
        phone_value = float(phone_value)
    except:
        phone_value = 0

    if target <= 0:
        return 0

    if phone_value >= target:
        return 100

    match = (phone_value / target) * 100

    return max(0, min(100, match))


# =========================================================
# 9. CALCULATE BUDGET MATCH
# =========================================================

def calculate_budget_match(phone_price, user_budget):

    try:
        phone_price = float(phone_price)
        user_budget = float(user_budget)
    except:
        return 0

    if user_budget <= 0:
        return 0

    # Phone is within budget
    if phone_price <= user_budget:
        return 100

    # Phone is above budget
    difference = phone_price - user_budget

    match = 100 - (
        difference / user_budget * 100
    )

    return max(0, min(100, match))


# =========================================================
# 10. MAIN FUZZY CALCULATION
# =========================================================

def calculate_phone_suitability(
    phone,
    user_budget,
    camera_preference,
    gaming_preference,
    battery_preference,
    performance_preference
):

    # -----------------------------------------------------
    # Calculate individual matching scores
    # -----------------------------------------------------

    budget_score = calculate_budget_match(
        phone['Price'],
        user_budget
    )

    camera_score = calculate_match(
        phone['Camera'],
        camera_preference
    )

    gaming_score = calculate_match(
        phone['Gaming'],
        gaming_preference
    )

    battery_score = calculate_match(
        phone['Battery'],
        battery_preference
    )

    performance_score = calculate_match(
        phone['Performance'],
        performance_preference
    )


    # -----------------------------------------------------
    # Create fuzzy simulation
    # -----------------------------------------------------

    simulation = ctrl.ControlSystemSimulation(
        phone_control
    )


    # -----------------------------------------------------
    # Give inputs to fuzzy system
    # -----------------------------------------------------

    simulation.input['budget_match'] = budget_score

    simulation.input['camera_match'] = camera_score

    simulation.input['gaming_match'] = gaming_score

    simulation.input['battery_match'] = battery_score

    simulation.input['performance_match'] = performance_score


    # -----------------------------------------------------
    # Fuzzy inference
    # -----------------------------------------------------

    try:

        simulation.compute()

        # Check whether fuzzy output exists
        if 'suitability' in simulation.output:

            return float(
                simulation.output['suitability']
            )

        # If no rule was activated
        return calculate_fallback_score(
            budget_score,
            camera_score,
            gaming_score,
            battery_score,
            performance_score
        )

    except Exception:

        # Safety fallback
        return calculate_fallback_score(
            budget_score,
            camera_score,
            gaming_score,
            battery_score,
            performance_score
        )


# =========================================================
# 11. FALLBACK SCORE
# =========================================================

def calculate_fallback_score(
    budget_score,
    camera_score,
    gaming_score,
    battery_score,
    performance_score
):

    # Weighted average
    score = (
        budget_score * 0.25 +
        camera_score * 0.20 +
        gaming_score * 0.20 +
        battery_score * 0.15 +
        performance_score * 0.20
    )

    return max(0, min(100, score))