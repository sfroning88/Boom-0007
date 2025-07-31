def classify_file(filename):
    import re
    from support.filetypes import journal_patterns
    
    for pattern in journal_patterns:
        if any(re.search(pattern, filename, re.IGNORECASE)):
            print("\nFound filetype: journal\n")
            return "journal"

    return "misc"
