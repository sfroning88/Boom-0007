def strip_nonabc(input_string):
    output_string = ''.join(c for c in input_string if c.isalpha())
    return output_string.lower()
