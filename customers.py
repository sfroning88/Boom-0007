def post_customers(files):
    try:
        # Hardcoded single customer
        file_key = list(files.keys())[1]
        sample_file = files[file_key]
        sample_extraction = sample_file['df']
        sample_customer = sample_extraction[0]
        print(sample_customer)

        return True
    
    except Exception as e:
        print(e)
        return False
