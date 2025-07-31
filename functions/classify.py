def classify_file(filename):
    import re
    
    from support.filetypes import journal_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in journal_patterns):
        print("\nFound filetype: journal\n")
        return "journal"

    from support.filetypes import customer_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in customer_patterns):
        print("\nFound filetype: customer\n")
        return "customer"

    from support.filetypes import vendor_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in vendor_patterns):
        print("\nFound filetype: vendor\n")
        return "vendor"

    return "misc"
