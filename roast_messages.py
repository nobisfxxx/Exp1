import random

roasts = [
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "If I had a dollar for every time you said something smart, I'd be poor.",
    "Are you always this dumb, or is today a special day for you?",
    "Your secrets are always safe with me. I never even listen when you tell me them.",
    "You bring everyone so much joy when you leave the room.",
    # Add more roasts here...
]

def get_random_roast(username):
    return f"{username}, {random.choice(roasts)}"
