# cy_device_spoofing.pyx

# Importing the random module using Cython's py_import
from random import choice

# Other code and function definitions

# Example usage of random.choice
def random_roast():
    ROASTS = [
        "You're like a cloud. When you disappear, it's a beautiful day!",
        "If you were a vegetable, you'd be a 'cabbage'.",
        "I would agree with you, but then we’d both be wrong.",
        "Your secrets are always safe with me. I never even listen when you tell me them.",
        "You bring everyone so much joy when you leave the room."
    ]
    return choice(ROASTS)  # Using random.choice here
