import random
import string

def generate_random_email(length=10, domain="example.com"):
    """Generates a random email address."""
    username_chars = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(username_chars) for _ in range(length))
    return f"{username}@{domain}"

print(generate_random_email(domain="mycompany.org"))