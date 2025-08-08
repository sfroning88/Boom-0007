def strip_nonabc(input_string):
    if not isinstance(input_string, str) or input_string is None:
        return ""

    output_string = ''.join(c for c in input_string if c.isalpha())
    return output_string.lower()

def strip_timestamp(date):
    import re
    return re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?$', '', date)

def days_timestamp(date, terms=30):
    if not isinstance(date, str) or date is None:
        return None

    from datetime import datetime, timedelta
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    due_date = date_obj + timedelta(days=terms)
    return due_date.strftime('%Y-%m-%d')
