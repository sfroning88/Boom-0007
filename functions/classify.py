def classify_file(filename):
    print("##############################_CLASS_BEGIN_##############################")
    
    import re
    
    from support.filetypes import journal_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in journal_patterns):
        print("CHECKPOINT: Found filetype: journal")
        print("##############################_CLASS_END_##############################")
        return "journal"

    from support.filetypes import customer_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in customer_patterns):
        print("CHECKPOINT: Found filetype: customer")
        print("##############################_CLASS_END_##############################")
        return "customer"

    from support.filetypes import vendor_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in vendor_patterns):
        print("CHECKPOINT: Found filetype: vendor")
        print("##############################_CLASS_END_##############################")
        return "vendor"

    from support.filetypes import account_patterns
    if any(re.search(pattern, filename, re.IGNORECASE) for pattern in account_patterns):
        print("CHECKPOINT: Found filetype: account")
        print("##############################_CLASS_END_##############################")
        return "account"

    print("WARNING: Failed to classify the file, please rename")
    print("##############################_CLASS_END_##############################")
    return "misc"
