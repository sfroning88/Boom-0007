def generate_code(filename):
    return str(abs(hash(filename)) % 1000000).zfill(6)
