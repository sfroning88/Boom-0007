ALLOWED_EXTENSIONS = ['csv', 'xls', 'xlsx']

def retrieve_extension(filename):
    # TODO(prod): Guard when no '.' present; return None and validate upstream.
    exte = '.' in filename and filename.rsplit('.', 1)[1].lower()
    return exte.strip().lower()  # TODO(prod): If exte is False/None, avoid .strip(); return None.
