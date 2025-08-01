def post_customers(files):
    import concurrent.futures
    from tqdm import tqdm
    try:
        # Determine customer file
        customer_file_key = None
        for single_file_key in files.keys():
            if files[single_file_key]['type'] == "customer" and files[single_file_key]['uploaded'] == False:
                customer_file_key = single_file_key
                break

        if customer_file_key is None:
            print("\nMissing customer file. Please upload file first.\n")
            return False

        customer_file = files[customer_file_key]
        customer_extraction = customer_file['df']

        # Concurrently post all customers
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            list(tqdm(executor.map(customer_threadsafe, list(customer_extraction.values())), total=len(list(customer_extraction.keys()))))

        return True
    
    except Exception as e:
        print(e)
        return False

def customer_threadsafe(one_customer):
    single_customer(one_customer)

def single_customer(one_customer):
    try:
        import re, os, requests
        from functions.generate import generate_code
        
        # Get OAuth tokens from environment or stored session
        access_token = os.environ.get('QBO_ACCESS_TOKEN')
        realm_id = os.environ.get('QBO_REALM_ID')
        
        if not access_token or not realm_id:
            print("Missing OAuth tokens. Please complete OAuth flow first.")
            return False
        
        # Clean and validate customer data
        display_name = str(one_customer.get('Customer', '')).strip()
        if not display_name:
            print("Customer name is required")
            return False
            
        customer = {
            "DisplayName": display_name
        }
        
        # Add optional fields only if they have valid data
        if one_customer.get('Primary Contact'):
            customer["Notes"] = str(one_customer['Primary Contact']).strip()
            
        if one_customer.get('Main Phone'):
            customer["PrimaryPhone"] = {
                "FreeFormNumber": str(one_customer['Main Phone']).strip()
            }
            
        if one_customer.get('Bill To'):
            customer["BillAddr"] = {
                "Line1": str(one_customer['Bill To']).strip()
            }
            
        # Clean company name if available
        if display_name:
            company_name = re.sub(r'[0-9\-\s]', '', display_name)
            if company_name.strip():
                customer["CompanyName"] = company_name.strip()

        # QBO API endpoint for creating customers
        base_url = 'https://sandbox-quickbooks.api.intuit.com'
        url = f'{base_url}/v3/company/{realm_id}/customer?minorversion=75'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(url, json=customer, headers=headers)
        
        if response.status_code >= 300:
            print(f"\nFailed to create customer {display_name}.\n")
            return False
        
        return True

    except Exception as e:
        print(e)
        return False
