def classify_file(filename):
    import re
    from support.filetypes import journal_patterns
    
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in journal_patterns):
        print("\nFound filetype: journal\n")
        return "journal"

    return "misc"
