from fuzzy_logic import calculate_phone_suitability


phone = {
    "Price": 29999,
    "Camera": 92,
    "Gaming": 75,
    "Battery": 85,
    "Performance": 90
}


score = calculate_phone_suitability(
    phone=phone,
    user_budget=30000,
    camera_preference="high",
    gaming_preference="high",
    battery_preference="high",
    performance_preference="high"
)


print("Phone Suitability Score:", round(score, 2))