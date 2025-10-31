# Test showing proper prediction logic

# AI course: CAT1=13.5/15 (90%), Quiz1=7/10 (70%)
# Current: 20.5/60 (34.2%)

# Prediction logic:
# 1. Estimate final internal based on current performance
# CAT1 = 13.5 (90%)
# Predict CAT2 = 13.5 * 0.95 = 12.8 (assume slight drop)
# Predict DA = 9.0 (90% of 10, matching CAT1 level)
# Quiz1 = 7.0 (actual)
# Predict Quiz2 = 8.5 (improved from Quiz1 70% to 85%)
# PREDICTED INTERNAL = 13.5 + 12.8 + 9.0 + 7.0 + 8.5 = 50.8/60 (84.7%)

# 2. Look at historical CORE_CSE courses with 80-90% internal:
# - Computer Programming: Python (82%) → A
# - Structured and Object-Oriented Programming (83%) → A  
# - Operating Systems (82%) → A
# - Computer Architecture (74%) → A

# 3. Predict grades based on historical FAT performance at that internal level:
# Optimistic: Match best performers (90%+ internal → S)
# Realistic: Average of 80-90% courses → A grade, ~85% total
# Pessimistic: Lower end → B grade, ~75% total

print("Artificial Intelligence Prediction:")
print("Current: CAT1=90%, Quiz1=70%")
print("Predicted Final Internal: 84.7%")
print()
print("Historical CORE_CSE at 80-90% internal:")
print("  → Typically get A grade (80-89% total)")
print("  → Some get S with strong FAT (90%+)")
print()
print("Predictions:")
print("  Optimistic: S grade (need 38-40/40 in FAT)")
print("  Realistic: A grade (need 32-34/40 in FAT)")  
print("  Pessimistic: B grade (need 26-28/40 in FAT)")
