def get_oauth_url(qbo_token=None, qbo_account=None, env_mode="sandbox"):
    if qbo_token is None or qbo_account is None:
        print("ERROR: Please set both your QBO token and account number in environment")
        return None
    
    from intuitlib.client import AuthClient
    from intuitlib.enums import Scopes

    # Use static ngrok domain for OAuth redirect URI
    redirect_uri = "https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback"
    auth_client = AuthClient(qbo_account, qbo_token, redirect_uri, environment=env_mode)
    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
        
    if len(url) > 0:
        print(f"SUCCESS: OAuth URL generated: {url}")  
        return url

    print("ERROR: Failed to generate OAuth URL")
    return None

def connect_qbo(qbo_token=None, qbo_account=None, auth_code=None, realm_id=None, env_mode="sandbox"):
    print("##############################_QBO_BEGIN_##############################")
    
    import requests, os
    from intuitlib.client import AuthClient

    # Use static ngrok domain for OAuth redirect URI
    redirect_uri = "https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback"
    auth_client = AuthClient(qbo_account, qbo_token, redirect_uri, environment=env_mode)
        
    if auth_code and realm_id:
        # Exchange auth code for bearer token and refresh token
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        print("CHECKPOINT: Bearer token and refresh token obtained successfully")
            
        # Store tokens for future use (in production, encrypt this)
        access_token = auth_client.access_token
        refresh_token = auth_client.refresh_token
        realm_id = auth_client.realm_id
            
        # Store in environment variables for API calls
        os.environ['QBO_ACCESS_TOKEN'] = access_token
        os.environ['QBO_REFRESH_TOKEN'] = refresh_token
        os.environ['QBO_REALM_ID'] = realm_id
            
        # Test the connection by fetching company info
        from support.config import env_mode
        base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
        
        url = '{0}/v3/company/{1}/companyinfo/{1}'.format(base_url, auth_client.realm_id)
        auth_header = 'Bearer {0}'.format(auth_client.access_token)
        headers = {
            'Authorization': auth_header,
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
            
        if response.status_code >= 300:
            print("ERROR: Missing auth_code or realm_id connection")
            print("##############################_QBO_END_##############################")
            return False

        print("CHECKPOINT: QBO connection verified successfully")
        print("##############################_QBO_END_##############################")
        return True
