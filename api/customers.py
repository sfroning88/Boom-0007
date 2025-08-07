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
        print("WARNING: Missing customer file. Please upload file first.")
        return False

    customer_file = files[customer_file_key]
    customer_extraction = customer_file['df']

    # Concurrently post all customers from customers
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(customer_threadsafe, list(customer_extraction.values())), total=len(list(customer_extraction.keys()))))

    print("##############################_POSTC_END_##############################")
    return True

def customer_threadsafe(one_customer):
    single_customer(one_customer)


def single_customer(one_customer):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.8, 1.2))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return False
        
    # Clean and validate customer data
    display_name = str(one_customer.get('Customer', '')).strip()
    if not display_name:
        print("ERROR: Customer name is required")
        return False
            
    customer = {
        "DisplayName": display_name,
        "Notes": one_customer['Primary Contact'] if one_customer['Primary Contact'] else "",
        "PrimaryPhone": { "FreeFormNumber": one_customer['Main Phone'] if one_customer['Main Phone'] else "" },
        "BillAddr": { "Line1": one_customer['Bill To'] if one_customer['Bill To'] else "" },
        "Balance": one_customer['Balance Total'],
        "OpenBalanceDate": "2024-12-31",
        "CompanyName": display_name
    }

    # QBO API endpoint for creating customers
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/customer?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=customer, headers=headers)
        
    if response.status_code >= 300:
        #print(f"WARNING: Did not post {display_name} (duplicate or Vendor)")
        return False
        
    return True
