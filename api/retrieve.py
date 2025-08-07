def get_database(query_mode=None):
    import os, requests

    if query_mode is None or not isinstance(query_mode,str):
        print("ERROR: Database failed to provide type for argument")
        return None

    if query_mode not in ["Customer", "Vendor", "Account"]:
        print("ERROR: Database provided wrong enum for argument")
        return None

    # Get OAuth tokens from environment
    access_token = os.environ.get('QBO_ACCESS_TOKEN')
    realm_id = os.environ.get('QBO_REALM_ID')
        
    if not access_token or not realm_id:
        print("WARNING: Missing OAuth tokens. Please complete OAuth flow first.")
        return None

    allowed_queries = {
        "Customer": "select DisplayName, Id FROM Customer MAXRESULTS 1000",
        "Vendor": "select DisplayName, Id FROM Vendor MAXRESULTS 1000",
        "Account": "select Name, Id, AccountType FROM Account MAXRESULTS 1000"
    }

     # QBO API endpoint for querying customers
    from support.config import env_mode
    base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
    url = f"{base_url}/v3/company/{realm_id}/query?query={allowed_queries[query_mode]}&minorversion=75"
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
        
    response = requests.get(url, headers=headers)
        
    if response.status_code >= 300:
        print(f"ERROR: Failed to retrieve {query_mode}s from QBO {response.text}")
        return None

    query_data = response.json()
    if 'QueryResponse' in query_data and query_mode in query_data['QueryResponse']:
        return query_data['QueryResponse']
    
    print(f"WARNING: No {query_mode}s found in QBO database")
    return None
