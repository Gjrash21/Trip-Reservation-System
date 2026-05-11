import random
import string


def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix


def generate_eticket():
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=8
        )
    )