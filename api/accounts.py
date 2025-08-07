def post_accounts(files):
    import concurrent.futures
    from tqdm import tqdm

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

    # Concurrently post all accounts
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(account_threadsafe, list(account_extraction.values())), total=len(list(account_extraction.keys()))))
    
    return True


def account_threadsafe(one_account):
    single_account(one_account)

def single_account(one_account):
    import os, requests, time, random

    # Respectful delay to the server
    time.sleep(random.uniform(0.8, 1.2))
        
    # Get OAuth tokens from environment or stored session
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens, please complete OAuth flow first")
        return False
            
    # Extract account data
    account_num = one_account['Num']
    account_name = one_account['Name']
    account_full = one_account['Full']

    # Create account object according to QBO API specification
    account = {
        "Name": account_name,
        "AcctNum": account_num,
        "Description": account_name,
        "AccountType": "Expense",
        "Active": True
    }

    # QBO API endpoint for creating accounts
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/account?minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    response = requests.post(url, json=account, headers=headers)
        
    if response.status_code >= 300:
        #print(f"WARNING: Failed to create account for {account_full} (duplicate)")
        return False
        
    #print(f"ACCOUNT: Posting account for {account_full")
    return True
