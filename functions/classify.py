def classify_file(filename):
    print("##############################_CLASS_BEGIN_##############################")
    
    import re
    
    from support.filetypes import journal_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in journal_patterns):
        print("Found filetype: journal")
        print("##############################_CLASS_END_##############################")
        return "journal"

    from support.filetypes import customer_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in customer_patterns):
        print("Found filetype: customer")
        print("##############################_CLASS_END_##############################")
        return "customer"

    from support.filetypes import vendor_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in vendor_patterns):
        print("Found filetype: vendor")
        print("##############################_CLASS_END_##############################")
        return "vendor"

    print("##############################_CLASS_END_##############################")
    return "misc"
