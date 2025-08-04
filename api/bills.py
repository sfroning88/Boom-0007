def post_bills(files):
    print("##############################_POSTB_BEGIN_##############################")

    import re
    import concurrent.futures
    from tqdm import tqdm

    # Determine journal file
    journal_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == "journal" and files[single_file_key]['uploaded'] == False:
            journal_file_key = single_file_key
            break

    if journal_file_key is None:
        print("WARNING: Missing journal file. Please upload file first.")
        return False

    journal_file = files[journal_file_key]
    journal_extraction = journal_file['df']

    # Collect the accounts payable Id
    from api.retrieve import get_expenses
    exp_id = get_expenses()

    # Remove any non bill transactions 
    from support.linetypes import bill_patterns
    bill_extraction = journal_extraction.copy()
    for key in list(bill_extraction.keys()):
        transaction_type = bill_extraction[key]['Type']
        if transaction_type.lower() == "bill":
            bill_extraction[key]['Exp_Id'] = exp_id
        else:
            bill_extraction.pop(key)

    print(f"CHECKPOINT: Found {len(list(bill_extraction.keys()))} bills to post.")

    # Clean vendor names to best match
    from api.resolve import resolve_vendors
    bill_extraction = resolve_vendors(bill_extraction)

    # Assign ids pulled from QBO
    from api.resolve import resolve_vend_ids
    bill_extraction = resolve_vend_ids(bill_extraction)

    # Concurrently post all bills
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        list(tqdm(executor.map(bill_threadsafe, list(bill_extraction.values())), total=len(list(bill_extraction.keys()))))
    
    print("##############################_POSTB_END_##############################")
    return True

def bill_threadsafe(one_bill):
    single_bill(one_bill)

def single_bill(one_bill):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.3, 0.8))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return False

    if one_bill['Id'] is None:
        print(f"WARNING: Could not post bill for {one_bill['Name']}")
        return False
            
    # Extract bill data
    bill_date = one_bill['Date']
    bill_number = one_bill['Num']
    memo = one_bill['Memo']
    amount = one_bill['Credit']
        
    # Create bill object according to QBO API specification
    bill = {
        "VendorRef": {
            "value": one_bill['Id']
        },
        "Line": [{
            "DetailType": "AccountBasedExpenseLineDetail",
            "Amount": amount,
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {
                "value": one_bill['Exp_Id'],
                "name": "Uncategorized Expense"
                }
            },
            "Description": memo if memo else "Bill line item"
        }]
    }
        
    # Add optional fields if available
    if bill_date:
        bill["DueDate"] = bill_date
        
    if bill_number:
        bill["DocNumber"] = bill_number
        
    if memo:
        bill["PrivateNote"] = memo

    # QBO API endpoint for creating bills
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/bill?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=bill, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to create bill for {one_bill['Name']}")
        return False
        
    #print(f"BILL: Posting bill for {one_bill['Name']}, Amount: ${amount}")
    return True
