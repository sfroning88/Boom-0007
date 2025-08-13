from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
import requests, os

# Test the connection by fetching company info
from support.config import env_mode

def get_oauth_url(qbo_token=None, qbo_account=None, env_mode="sandbox"):
    # TODO(prod): Fetch redirect_uri from config/env (e.g., QBO_REDIRECT_URI); never hardcode domains.
    # TODO(prod): Generate and include an OAuth 'state' parameter; persist it server-side and verify in callback to prevent CSRF.
    # TODO(prod): Make scopes configurable; consider least-privilege and future expansion.

    if qbo_token is None or qbo_account is None:
        print("ERROR: Please set both your QBO token and account number in environment")
        return None
    
    

    # Use static ngrok domain for OAuth redirect URI
    redirect_uri = "https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback"  # TODO(prod): replace with env/config
    auth_client = AuthClient(qbo_account, qbo_token, redirect_uri, environment=env_mode)
    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])  # TODO(prod): pass 'state' here and store server-side
    
    if len(url) > 0:
        print(f"SUCCESS: OAuth URL generated: {url}")  
        return url

    print("ERROR: Failed to generate OAuth URL")
    return None

def connect_qbo(qbo_token=None, qbo_account=None, auth_code=None, realm_id=None, env_mode="sandbox"):
    print("##############################_QBO_BEGIN_##############################")
    
    

    # TODO(prod): Validate and compare OAuth 'state' from callback to stored server-side state; reject mismatches.

    # Use static ngrok domain for OAuth redirect URI
    redirect_uri = "https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback"  # TODO(prod): replace with env/config
    auth_client = AuthClient(qbo_account, qbo_token, redirect_uri, environment=env_mode)
        
    if auth_code and realm_id:
        # Exchange auth code for bearer token and refresh token
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        print("CHECKPOINT: Bearer token and refresh token obtained successfully")
            
        # Store tokens for future use (in production, encrypt this)
        access_token = auth_client.access_token
        refresh_token = auth_client.refresh_token
        realm_id = auth_client.realm_id

        # TODO(prod): Persist tokens in DB (encrypted) with expires_at; do NOT store in process env.
        os.environ['QBO_ACCESS_TOKEN'] = access_token  # TODO(remove): replace with DB persistence
        os.environ['QBO_REFRESH_TOKEN'] = refresh_token  # TODO(remove)
        os.environ['QBO_REALM_ID'] = realm_id  # TODO(remove)

        # TODO(prod): Centralize QBO client (base_url + headers) + auto-refresh on 401 with retry-once.

        base_url = 'https://quickbooks.api.intuit.com' if env_mode == "production" else 'https://sandbox-quickbooks.api.intuit.com'
        
        url = '{0}/v3/company/{1}/companyinfo/{1}'.format(base_url, auth_client.realm_id)
        auth_header = 'Bearer {0}'.format(auth_client.access_token)
        headers = {
            'Authorization': auth_header,
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
            
        if response.status_code >= 300:
            # TODO(prod): Log structured error incl. response.json(); do not leak secrets.
            print("ERROR: Missing auth_code or realm_id connection")
            print("##############################_QBO_END_##############################")
            return False

        print("CHECKPOINT: QBO connection verified successfully")
        print("##############################_QBO_END_##############################")
        return True