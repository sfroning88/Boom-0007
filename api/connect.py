def get_oauth_url(qbo_token, qbo_account):
    from intuitlib.client import AuthClient
    from intuitlib.enums import Scopes

    try:
        # Generate OAuth authorization URL for user to authorize once
        redirect_uri = "http://localhost:5000/oauth/callback"
        auth_client = AuthClient(qbo_account, qbo_token, redirect_uri, environment="sandbox")
        url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
        
        print(f"\nOAuth URL generated: {url}\n")
        return url

    except Exception as e:
        print(e)
        return None

def connect_qbo(qbo_token, qbo_account, auth_code=None, realm_id=None):
    import requests
    from intuitlib.client import AuthClient

    try:
        # Complete QBO connection with auth code and store refresh token
        redirect_uri = "http://localhost:5000/oauth/callback"
        auth_client = AuthClient(qbo_account, qbo_token, redirect_uri, environment="sandbox")
        
        if auth_code and realm_id:
            # Exchange auth code for bearer token and refresh token
            auth_client.get_bearer_token(auth_code, realm_id=realm_id)
            print("\nBearer token and refresh token obtained successfully\n")
            
            # Store refresh token for future use (in production, encrypt this)
            refresh_token = auth_client.refresh_token
            print(f"\nRefresh token stored: {refresh_token[:20]}...\n")
            
            # Test the connection by fetching company info
            base_url = 'https://sandbox-quickbooks.api.intuit.com'
            url = '{0}/v3/company/{1}/companyinfo/{1}'.format(base_url, auth_client.realm_id)
            auth_header = 'Bearer {0}'.format(auth_client.access_token)
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                print("\nQBO connection verified successfully\n")
                return True
            else:
                print(response.status_code, response.text)
                return False
        else:
            print("\nMissing auth_code or realm_id\n")
            return False

    except Exception as e:
        print(e)
        return False
