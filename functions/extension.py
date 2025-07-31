ALLOWED_EXTENSIONS = ['csv', 'xls', 'xlsx']

def retrieve_extension(filename):
    exte = '.' in filename and filename.rsplit('.', 1)[1].lower()
    return exte.strip().lower()

def strip_timestamp(date):
    import re
    return re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?$', '', date)
