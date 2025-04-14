# cy_device_spoofing.pyx

import random
import string

# Function to generate random device fingerprint
def generate_device_fingerprint():
    """Generate a random fingerprint for device spoofing."""
    manufacturers = ['Samsung', 'Apple', 'Google', 'Xiaomi', 'Infinix']
    models = ['GT 10 Pro', 'Galaxy S20', 'Pixel 6', 'Redmi Note 11', 'Mi 11']

    manufacturer = random.choice(manufacturers)
    model = random.choice(models)
    android_version = random.choice([13, 14, 15])  # Choose a random Android version
    resolution = random.choice(['1080x2400', '1440x3200', '1080x2340'])
    cpu = random.choice(['mt6893', 'snapdragon_888', 'mediatek_dimensity1200'])

    # Generate random values for other fields
    dpi = random.choice([320, 480])
    device_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    fingerprint = {
        "manufacturer": manufacturer,
        "model": model,
        "android_version": android_version,
        "resolution": resolution,
        "cpu": cpu,
        "dpi": dpi,
        "device_id": device_id,
    }

    return fingerprint
