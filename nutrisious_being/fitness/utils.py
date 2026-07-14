def calculate_bmi(weight, height):
    """
    Calculates Body Mass Index (BMI) and returns (bmi_value, category).
    weight is in kg, height is in cm.
    """
    if not weight or not height or height <= 0:
        return 0, "Unknown"
    
    height_m = float(height) / 100.0
    bmi = float(weight) / (height_m ** 2)
    bmi = round(bmi, 1)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
        
    return bmi, category


def calculate_bmr(gender, weight, height, age):
    """
    Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.
    weight in kg, height in cm, age in years.
    """
    w = float(weight)
    h = float(height)
    a = int(age)
    
    if gender == 'M':
        return round(10.0 * w + 6.25 * h - 5.0 * a + 5)
    elif gender == 'F':
        return round(10.0 * w + 6.25 * h - 5.0 * a - 161)
    else:
        # Default/Other: average of male and female BMR
        return round(10.0 * w + 6.25 * h - 5.0 * a - 78)


def calculate_tdee(bmr, activity_level):
    """
    Calculates Total Daily Energy Expenditure (TDEE) based on BMR and activity level.
    """
    factors = {
        'SED': 1.2,      # Sedentary
        'LIG': 1.375,    # Lightly active
        'MOD': 1.55,     # Moderately active
        'ACT': 1.725,    # Very active
        'EXT': 1.9,      # Extra active
    }
    factor = factors.get(activity_level, 1.2)
    return round(bmr * factor)


def calculate_targets(tdee, goal):
    """
    Calculates target calories and macronutrients (protein, carbs, fats in grams) based on TDEE and fitness goal.
    Returns a dict with targets.
    """
    # 1. Target Calories
    if goal == 'LOSE':
        # Deficit of 500 kcal, floor at 1200 kcal for safety
        target_calories = max(tdee - 500, 1200)
    elif goal == 'GAIN':
        # Surplus of 500 kcal
        target_calories = tdee + 500
    else:
        # Maintain
        target_calories = tdee
        
    # 2. Target Macros percentages
    # Calories densities: Protein=4, Carbs=4, Fats=9
    if goal == 'LOSE':
        p_pct, c_pct, f_pct = 0.30, 0.40, 0.30
    elif goal == 'GAIN':
        p_pct, c_pct, f_pct = 0.30, 0.50, 0.20
    else:
        # Maintain
        p_pct, c_pct, f_pct = 0.25, 0.45, 0.30
        
    protein_g = round((target_calories * p_pct) / 4)
    carbs_g = round((target_calories * c_pct) / 4)
    fats_g = round((target_calories * f_pct) / 9)
    
    return {
        'calories': target_calories,
        'protein': protein_g,
        'carbs': carbs_g,
        'fats': fats_g
    }
