def post_vendors(files):
    print("##############################_POSTV_BEGIN_##############################")
    
    import concurrent.futures
    from tqdm import tqdm

    # Determine vendor file
    vendor_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == "vendor" and files[single_file_key]['uploaded'] == False:
            vendor_file_key = single_file_key
            break

    if vendor_file_key is None:
        print("Missing vendor file. Please upload file first.")
        return False

    vendor_file = files[vendor_file_key]
    vendor_extraction = vendor_file['df']

    # Concurrently post all vendors from vendors
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        list(tqdm(executor.map(vendor_threadsafe, list(vendor_extraction.values())), total=len(list(vendor_extraction.keys()))))

    print("##############################_POSTV_END_##############################")
    return True

def vendor_threadsafe(one_vendor):
    single_vendor(one_vendor)

def single_vendor(one_vendor):
    import os, requests
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("Missing OAuth tokens. Please complete OAuth flow first.")
        return False
        
    # Clean and validate vendor data
    display_name = str(one_vendor.get('Vendor', '')).strip()
    if not display_name:
        print("Vendor name is required")
        return False
            
    vendor = {
        "DisplayName": display_name
    }
        
    # Add optional fields only if they have valid data
    if one_vendor.get('Primary Contact'):
        vendor["Notes"] = str(one_vendor['Primary Contact']).strip()

    if one_vendor.get('Account #'):
        vendor["AcctNum"] = str(one_vendor['Account #']).strip()

    if one_vendor.get('Main Phone'):
        vendor["PrimaryPhone"] = {
            "FreeFormNumber": str(one_vendor['Main Phone']).strip()
        }
            
    if one_vendor.get('Bill From'):
        vendor["BillAddr"] = {
            "Line1": str(one_vendor['Bill From']).strip()
        }

    if one_vendor.get('Fax'):
        vendor["Fax"] = str(one_vendor['Fax']).strip()

    if one_vendor.get('Balance Total'):
        vendor["Balance"] = str(one_vendor['Balance Total']).strip()
            
    # Clean company name if available
    if display_name:
        vendor["CompanyName"] = display_name

    # QBO API endpoint for creating vendors
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/vendor?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=vendor, headers=headers)
        
    if response.status_code >= 300:
        return False
        
    return True

def get_vendors():
    import os, requests
        
    # Get OAuth tokens from environment
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("Missing OAuth tokens. Please complete OAuth flow first.")
        return None
        
    # QBO API endpoint for querying customers
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/query?query=select DisplayName, Id FROM Vendor MAXRESULTS 1000&minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
        
    if response.status_code < 300:
        vendors_data = response.json()
        if 'QueryResponse' in vendors_data and 'Vendor' in vendors_data['QueryResponse']:
            vendors = vendors_data['QueryResponse']
            return vendors
        else:
            print("No vendors found in QBO database.")
            return {}
    else:
        print(f"Failed to retrieve vendors: {response.text}")
        return None
