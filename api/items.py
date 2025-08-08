def post_items(files=None, begin_date="2025-01-01", end_date="2025-01-31", item_mode=None):
    print("##############################_POST_BEGIN_##############################")
    if files is None:
        print("WARNING: No files have been uploaded, please upload files")
        return False
    
    if item_mode is None:
        print("ERROR: No item mode was passed into posting function")
        return False

    if item_mode not in ["invoice", "bill"]:
        print("ERROR: Incorrect enum mode passed into posting function")
        return False

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

    if item_mode == "bill":
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

    # Remove any non item transactions or older transactions
    from functions.stripping import strip_nonabc
    item_extraction = journal_extraction.copy()
    for key in list(item_extraction.keys()):
        transaction_type = item_extraction[key]['Type'].lower()
        transaction_date = item_extraction[key]['Date']
        transaction_amount = item_extraction[key]['Amount']

        if transaction_type != item_mode:
            item_extraction.pop(key)
            continue

        if transaction_date < begin_date or transaction_date > end_date:
            item_extraction.pop(key)
            continue

        if transaction_amount == 0.0:
            item_extraction.pop(key)
            continue

        if item_mode == "bill":
            transaction_account = strip_nonabc(item_extraction[key]['Account'])
            if transaction_account not in account_olds:
                print(f"WARNING: Bill tied to account {item_extraction[key]['Account']} does not exist in Chart of Accounts")
                item_extraction.pop(key)
                continue

            for account_object in list(account_extraction.values()):
                if transaction_account == account_object['Old']:
                    qbo_account = account_object['Name']
        
            if qbo_account not in list(exp_id_mapping.keys()):
                print(f"WARNING: Bill tied to account {item_extraction[key]['Account']} does not exist in QBO")
                item_extraction.pop(key)
                continue
        
            item_extraction[key]['Exp_Id'] = exp_id_mapping[qbo_account]

    print(f"CHECKPOINT: Found {len(list(item_extraction.keys()))} {item_mode}s to post from {begin_date} to {end_date}")

    # Clean object names to best match
    from api.resolve import resolve_objects
    object_mode = "Vendor" if item_mode == "bill" else "Customer"
    item_extraction = resolve_objects(extraction=item_extraction, object_mode=object_mode)

    if item_extraction is None:
        return False

    # Assign ids pulled from QBO
    from api.resolve import resolve_ids
    item_extraction = resolve_ids(extraction=item_extraction, object_mode=object_mode)

    if item_extraction is None:
        return False

    # Concurrently post all items
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(item_threadsafe, list(item_extraction.values())), total=len(list(item_extraction.keys()))))
    
    print("##############################_POSTB_END_##############################")
    return True

def item_threadsafe(one_item):
    post_one(one_item)

def post_one(one_item):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.8, 1.2))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens, please complete OAuth flow first")
        return False

    if one_item['Id'] is None:
        print(f"ERROR: Missing Id for {one_item['Name']}, Amount: ${one_item['Amount']}")
        return False

    item_mode = one_item['Type'].lower()
    item_name = one_item['Name']
    item_id = one_item['Id']
    item_date = one_item['Date']
    item_number = one_item['Num']
    item_memo = one_item['Memo']
    item_amount = one_item['Amount']

     # net 30 terms default
    from functions.stripping import days_timestamp
    item_due_date = days_timestamp(item_date, 30)

    if item_mode == "invoice":
        item_payload = {
        "CustomerRef": {
            "value": item_id
        },
        "Line": [{
            "DetailType": "SalesItemLineDetail",
            "SalesItemLineDetail": {
                "ServiceDate": item_date
            },
            "Amount": item_amount,
            "Description": item_memo if item_memo else "Invoice line item"
        }],
        "TotalAmt": item_amount,
        "TxnDate": item_date,
        "DueDate": item_due_date if item_due_date else item_date,
        "DocNumber": item_number,
        "PrivateNote": item_memo if item_memo else "Uncategorized Income"
    }
    
    elif item_mode == "bill":
        item_account = one_item['Account']
        item_exp_id = one_item['Exp_Id']

        # Create bill object according to QBO API specification
        item_payload = {
            "VendorRef": {
                "value": item_id
            },
            "Line": [{
                "DetailType": "AccountBasedExpenseLineDetail",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                    "value": item_exp_id,
                    "name": item_account
                    }
                },
                "Amount": item_amount,
                "Description": item_memo if item_memo else "Uncategorized Expense"
            }],
            "TotalAmt": item_amount,
            "TxnDate": item_date,
            "DueDate": item_due_date if item_due_date else item_date,
            "DocNumber": item_number,
            "PrivateNote": item_memo if item_memo else "Uncategorized Expense"
        }

    # QBO API endpoint for creating items
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/{item_mode}?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=item_payload, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to create {item_mode} for {item_name}, Amount: ${item_amount}")
        return False
        
    #print(f"{item_mode}.upper(): Posting {item_mode} for {item_name}, Amount: ${item_amount}")
    return True
