def post_customers(files):
    print("##############################_POSTC_BEGIN_##############################")
    
    import concurrent.futures
    from tqdm import tqdm

    # Determine customer file
    customer_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == "customer" and files[single_file_key]['uploaded'] == False:
            customer_file_key = single_file_key
            break

    if customer_file_key is None:
        print("Missing customer file. Please upload file first.")
        return False

    customer_file = files[customer_file_key]
    customer_extraction = customer_file['df']

    # Concurrently post all customers from customers
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        list(tqdm(executor.map(customer_threadsafe, list(customer_extraction.values())), total=len(list(customer_extraction.keys()))))

    print("##############################_POSTC_END_##############################")
    return True

def customer_threadsafe(one_customer):
    single_customer(one_customer)

def single_customer(one_customer):
    import os, requests
        
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

    if one_customer.get('Fax'):
        customer["Fax"] = str(one_customer['Fax']).strip()

    if one_customer.get('Balance Total'):
        customer["Balance"] = str(one_customer['Balance Total']).strip()
            
    # Clean company name if available
    if display_name:
        customer["CompanyName"] = display_name

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
        return False
        
    return True

def get_customers():
    import os, requests
        
    # Get OAuth tokens from environment
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("Missing OAuth tokens. Please complete OAuth flow first.")
        return None
        
    # QBO API endpoint for querying customers
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/query?query=select DisplayName, Id FROM Customer MAXRESULTS 1000&minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
        
    response = requests.get(url, headers=headers)
        
    if response.status_code < 300:
        customers_data = response.json()
        if 'QueryResponse' in customers_data and 'Customer' in customers_data['QueryResponse']:
            customers = customers_data['QueryResponse']
            return customers
        else:
            print("No customers found in QBO database.")
            return {}
    else:
        print(f"Failed to retrieve customers: {response.text}")
        return None
