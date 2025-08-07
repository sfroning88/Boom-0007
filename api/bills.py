def post_bills(files, begin_date="2025-01-01", end_date="2025-01-31"):
    print("##############################_POSTB_BEGIN_##############################")

    import concurrent.futures
    from tqdm import tqdm

    # Determine journal file
    journal_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == "journal" and files[single_file_key]['uploaded'] == False:
            journal_file_key = single_file_key
            break

    if journal_file_key is None:
        print("WARNING: Missing journal file, please upload file first")
        return False

    journal_file = files[journal_file_key]
    journal_extraction = journal_file['df']

    # Determine accounts file
    account_file_key = None
    for single_file_key in files.keys():
        if files[single_file_key]['type'] == "account" and files[single_file_key]['uploaded'] == False:
            account_file_key = single_file_key
            break

    if account_file_key is None:
        print("WARNING: Missing accounts file, please upload file first")
        return False

    account_file = files[account_file_key]
    account_extraction = account_file['df']

    account_olds = []
    for account_object in list(account_extraction.values()):
        account_olds.append(account_object['Old'])

    # Collect the expense account ids
    from api.retrieve import get_database
    accounts_pre = get_database(query_mode="Account")
    if accounts_pre is None or 'Account' not in list(accounts_pre.keys()):
        print("WARNING: Please upload Chart of Accounts to QBO before posting bills")
        return False

    accounts_post = accounts_pre['Account'] if accounts_pre is not None else None

    exp_id_mapping = {}
    for account_object in accounts_post:
        exp_id_mapping[account_object['Name']] = account_object['Id']

    # Remove any non bill transactions or older transactions
    from functions.stripping import strip_nonabc
    bill_extraction = journal_extraction.copy()
    for key in list(bill_extraction.keys()):
        transaction_type = bill_extraction[key]['Type'].lower()
        transaction_date = bill_extraction[key]['Date']
        transaction_amount = bill_extraction[key]['Amount']
        transaction_account = strip_nonabc(bill_extraction[key]['Account'])

        if transaction_type not in ["bill"]:
            bill_extraction.pop(key)
            continue

        if transaction_date < begin_date or transaction_date > end_date:
            bill_extraction.pop(key)
            continue

        if transaction_amount == 0.0:
            bill_extraction.pop(key)
            continue

        if transaction_account not in account_olds:
            print(f"WARNING: Bill tied to account {bill_extraction[key]['Account']} does not exist in Chart of Accounts")
            bill_extraction.pop(key)
            continue

        for account_object in list(account_extraction.values()):
            if transaction_account == account_object['Old']:
                qbo_account = account_object['Name']
        
        if qbo_account not in list(exp_id_mapping.keys()):
            print(f"WARNING: Bill tied to account {bill_extraction[key]['Account']} does not exist in QBO")
            bill_extraction.pop(key)
            continue
        
        bill_extraction[key]['Exp_Id'] = exp_id_mapping[qbo_account]

    print(f"CHECKPOINT: Found {len(list(bill_extraction.keys()))} bills to post from {begin_date} to {end_date}")

    # Clean vendor names to best match
    from api.resolve import resolve_vendors
    bill_extraction = resolve_vendors(bill_extraction)

    if bill_extraction is None:
        return False

    # Assign ids pulled from QBO
    from api.resolve import resolve_vend_ids
    bill_extraction = resolve_vend_ids(bill_extraction)

    # Concurrently post all bills
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(bill_threadsafe, list(bill_extraction.values())), total=len(list(bill_extraction.keys()))))
    
    print("##############################_POSTB_END_##############################")
    return True

def bill_threadsafe(one_bill):
    single_bill(one_bill)

def single_bill(one_bill):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.8, 1.2))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return False

    if one_bill['Id'] is None:
        print(f"ERROR: Missing Id for {one_bill['Name']}, Amount: ${one_bill['Amount']}")
        return False
            
    # Extract bill data
    bill_name = one_bill['Name']
    bill_id = one_bill['Id']
    bill_date = one_bill['Date']
    bill_number = one_bill['Num']
    bill_memo = one_bill['Memo']
    bill_amount = one_bill['Amount']
    bill_account = one_bill['Account']
    bill_exp_id = one_bill['Exp_Id']

    # net 30 terms default
    from functions.stripping import days_timestamp
    bill_due_date = days_timestamp(bill_date, 30)

    # Create bill object according to QBO API specification
    bill = {
        "VendorRef": {
            "value": bill_id
        },
        "Line": [{
            "DetailType": "AccountBasedExpenseLineDetail",
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {
                "value": bill_exp_id,
                "name": bill_account
                }
            },
            "Amount": bill_amount,
            "Description": bill_memo if bill_memo else "Uncategorized Expense"
        }],
        "TotalAmt": bill_amount,
        "TxnDate": bill_date,
        "DueDate": bill_due_date if bill_due_date else bill_date,
        "DocNumber": bill_number,
        "PrivateNote": bill_memo if bill_memo else "Uncategorized Expense"
    }

    # QBO API endpoint for creating bills
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/bill?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=bill, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to create bill for {bill_name}, Amount: ${bill_amount}")
        return False
        
    #print(f"BILL: Posting bill for {bill_name}, Amount: ${bill_amount}")
    return True
