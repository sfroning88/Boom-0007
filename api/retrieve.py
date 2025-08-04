def get_customers():
    import os, requests
        
    # Get OAuth tokens from environment
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return None
        
    # QBO API endpoint for querying customers
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/query?query=select DisplayName, Id FROM Customer MAXRESULTS 1000&minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
        
    response = requests.get(url, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERORR: Failed to retrieve customers from QBO")
        return None

    customers_data = response.json()
    if 'QueryResponse' in customers_data and 'Customer' in customers_data['QueryResponse']:
        customers = customers_data['QueryResponse']
        return customers
    else:
        print("WARNING: No customers found in QBO database.")
        return {}

def get_vendors():
    import os, requests
        
    # Get OAuth tokens from environment
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return None
        
    # QBO API endpoint for querying customers
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/query?query=select DisplayName, Id FROM Vendor MAXRESULTS 1000&minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to retrieve vendors from QBO")
        return None

    vendors_data = response.json()
    if 'QueryResponse' in vendors_data and 'Vendor' in vendors_data['QueryResponse']:
        vendors = vendors_data['QueryResponse']
        return vendors
    else:
        print("WARNING: No vendors found in QBO database.")
        return {}

def get_expenses():
    import os, requests
        
    # Get OAuth tokens from environment
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return None
        
    # QBO API endpoint for querying accounts
    base_url = 'https://sandbox-quickbooks.api.intuit.com'
    url = f'{base_url}/v3/company/{realm_id}/query?query=select Id, Name, AccountType FROM Account&minorversion=75'
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to retrieve expense account from QBO")
        return None
    
    accounts_data = response.json()
    if 'QueryResponse' in accounts_data and 'Account' in accounts_data['QueryResponse']:
            accounts = accounts_data['QueryResponse']
            accounts = accounts['Account']
            for account_object in accounts:
                if account_object['Name'] ==  "Uncategorized Expense":
                    return account_object['Id']
    else:
            print("WARNING: No expense accounts found in QBO database.")
            return None
