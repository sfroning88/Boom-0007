def post_objects(files=None, object_mode=None):
    print("##############################_POST_BEGIN_##############################")
    if files is None:
        print("WARNING: No files have been uploaded, please upload files")
        return False
    
    if object_mode is None:
        print("ERROR: No item mode was passed into posting function")
        return False

    if object_mode not in ["customer", "vendor", "account"]:
        print("ERROR: Incorrect enum mode passed into posting function")
        return False

    import concurrent.futures
    from tqdm import tqdm

    # Determine object file
    object_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == object_mode and files[single_file_key]['uploaded'] == False:
            object_file_key = single_file_key
            break

    if object_file_key is None:
        print(f"WARNING: Missing {object_mode} file, please upload file first.")
        return False

    object_file = files[object_file_key]
    object_extraction = object_file['df']

    # Concurrently post all objects
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(object_threadsafe, list(object_extraction.values())), total=len(list(object_extraction.keys()))))

    print("##############################_POST_END_##############################")
    return True

def object_threadsafe(one_object):
    post_one(one_object)

def post_one(one_object):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.8, 1.2))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens, please complete OAuth flow first")
        return False

    if 'Vendor' in list(one_object.keys()):
        object_mode = 'Vendor'
    elif 'Customer' in list(one_object.keys()):
        object_mode = 'Customer'
    elif 'Account' in list(one_object.keys()):
        object_mode = 'Account'

    # Clean and validate object data
    display_name = one_object[object_mode]
    if not display_name:
        print(f"ERROR: Entry did not contain {object_mode}, skipped")
        return False

    if object_mode == 'Vendor':  
        # Create vendor object according to QBO API specification  
        object_payload = {
            "DisplayName": display_name,
            "Notes": one_object['Primary Contact'] if one_object['Primary Contact'] else "",
            "AcctNum": one_object['Account #'] if one_object['Account #'] else "",
            "PrimaryPhone": { "FreeFormNumber": one_object['Main Phone'] if one_object['Main Phone'] else "" },
            "BillAddr": { "Line1": one_object['Bill From'] if one_object['Bill From'] else "" },
            "Balance": one_object['Balance Total'],
            "OpenBalanceDate": "2024-12-31",
            "CompanyName": display_name,
            "Active": True
        }
    
    elif object_mode == 'Customer':
        # Create customer object according to QBO API specification
        object_payload = {
            "DisplayName": display_name,
            "Notes": one_object['Primary Contact'] if one_object['Primary Contact'] else "",
            "PrimaryPhone": { "FreeFormNumber": one_object['Main Phone'] if one_object['Main Phone'] else "" },
            "BillAddr": { "Line1": one_object['Bill To'] if one_object['Bill To'] else "" },
            "Balance": one_object['Balance Total'],
            "OpenBalanceDate": "2024-12-31",
            "CompanyName": display_name,
            "Active": True
        }

    elif object_mode == 'Account':
        # Create account object according to QBO API specification
        object_payload = {
            "Name": display_name,
            "AcctNum": one_object['Num'],
            "Description": display_name,
            "AccountType": "Expense",
            "Active": True
        }

    # QBO API endpoint for creating objects
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/{object_mode.lower()}?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=object_payload, headers=headers)
        
    if response.status_code >= 300:
        print(f"WARNING: Did not post {display_name} (duplicate object)")
        return False
        
    return True
