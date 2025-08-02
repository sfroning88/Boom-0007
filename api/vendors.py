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
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
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
        print(f"Duplicate, skipping {display_name}....")
        return False
        
    return True

def get_vendors():
    try:
        import os, requests
        
        # Get OAuth tokens from environment
        access_token = os.environ.get('QBO_ACCESS_TOKEN')
        realm_id = os.environ.get('QBO_REALM_ID')
        
        if not access_token or not realm_id:
            print("Missing OAuth tokens. Please complete OAuth flow first.")
            return None
        
        # QBO API endpoint for querying vendors
        base_url = 'https://sandbox-quickbooks.api.intuit.com'
        url = f'{base_url}/v3/company/{realm_id}/query?query=select DisplayName, Id FROM Vendor&minorversion=75'
        
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

    except Exception as e:
        print(e)
        return None

def clean_vendors(invoices_extracted):
    import re

    vendors_existing = []
    ids_existing = []
    vendors_pre = get_vendors()
    vendors_post = vendors_pre['Vendor']
    for vendor in vendors_post:
        vendors_existing.append(vendor['DisplayName'])
        ids_existing.append(vendor['Id'])
    if len(vendors_existing) == 0:
        return invoices_extracted

    print(f"Vendors len = {len(vendors_existing)}, Ids len = {len(ids_existing)}")

    for vendor_object in list(invoices_extracted.values()):
        match_flag = False
        invoice_vendor_name = vendor_object['Name']
        if not invoice_vendor_name:
            continue
        
        id_index = 0
        for vendor_name in vendors_existing:
            if match_flag == False:

                # Check for exact or partial match
                if re.search(invoice_vendor_name, vendor_name, re.IGNORECASE):
                    vendor_object['Name'] = vendor_name
                    vendor_object['Id'] = ids_existing[id_index] if id_index < len(ids_existing) else None
                    match_flag = True
                    break

                elif re.search(vendor_name, invoice_vendor_name, re.IGNORECASE):
                    vendor_object['Name'] = vendor_name
                    vendor_object['Id'] = ids_existing[id_index] if id_index < len(ids_existing) else None
                    match_flag = True
                    break
            id_index += 1
        
        # Create dummy vendor object and add to database
        if match_flag == False:
            dummy_vendor = {
                'Vendor': invoice_vendor_name,
                'Bill To': '',
                'Primary Contact': '',
                'Main Phone': '',
                'Fax': '',
                'Balance Total': 0.0
            }
            
            print(f"Adding new vendor: {invoice_vendor_name}")
            try:
                single_vendor(dummy_vendor)
            except Exception as e:
                print(e)
            
            if invoice_vendor_name not in vendors_existing:
                vendors_existing.append(invoice_vendor_name)

    return invoices_extracted
