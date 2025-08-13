import os, sys
from flask import Flask, render_template, jsonify, request
from ngrok import connect

# create a Flask app
# create a Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')  # TODO(prod): require via env; no default; rotate regularly.

# TODO(prod): Replace print with structured logging (json) across app; add request IDs/correlation IDs.
# TODO(prod): Add authentication/authorization for all POST routes (admin-only).
# TODO(prod): Move runtime configuration to a settings module (pydantic/dotenv) and remove hardcoded domains.

# get the Ngrok token
ngrok_token = os.environ.get('NGROK_API_TOKEN')

@app.route('/')
def home():
    # Render base home template
    return render_template('chat.html')

@app.route('/SET_GLOBAL_VARS', methods=['POST'])
@app.route('/SET_GLOBAL_VARS', methods=['POST'])
def SET_GLOBAL_VARS():
    import support.config
    data = request.get_json()
    # TODO(prod): Validate payload with schema (pydantic); enforce date formats; begin_date <= end_date.
    # TODO(prod): Persist per-user/per-client in DB, not module globals; avoid cross-user bleed in multi-worker.
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    env_mode = data.get('env_mode')
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    
    if env_mode and env_mode in ['sandbox', 'production']:
        support.config.env_mode = env_mode
    
    if begin_date:
        support.config.begin_date = begin_date
    
    if end_date:
        support.config.end_date = end_date
    
    return jsonify({'success': True, 'message': 'Global variables updated successfully'}), 200

# connecting first time to qbo for authorization
@app.route('/CONNECT_QBO', methods=['POST'])
def CONNECT_QBO():
    import support.config

    # TODO(prod): Generate OAuth 'state' and persist in session/DB; pass to get_oauth_url; validate on callback.
    # TODO(prod): Read redirect_uri and env_mode from centralized settings.

    from api.connect import get_oauth_url
    oauth_url = get_oauth_url(support.config.qbo_token, support.config.qbo_account, support.config.env_mode)
        
    if oauth_url:
        return jsonify({'success': True, 'message': 'Redirecting to QBO authorization...', 'redirect_url': oauth_url}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to generate OAuth URL'}), 400

@app.route('/oauth/callback')
def oauth_callback():
    import support.config
    auth_code = request.args.get('code')
    realm_id = request.args.get('realmId')
    # TODO(prod): Read 'state' and validate against stored value; reject if mismatch; clear one-time state.

    if not auth_code or not realm_id:
        return jsonify({'success': False, 'message': 'Missing authorization code or realm ID'}), 400
        
    # Connect to QBO with the received auth code and store refresh token
    from api.connect import connect_qbo
    success = connect_qbo(support.config.qbo_token, support.config.qbo_account, auth_code, realm_id, support.config.env_mode)

    # TODO(prod): On success, persist tokens to DB; do not keep in env; schedule refresh before expiry; mask tokens in logs.
        
    if success:
        # Show success page that will update the main app
        return render_template('oauth_success.html', message='QBO connection established successfully!')
    else:
        return render_template('oauth_error.html', message='Failed to establish QBO connection')

# uploading different QBD files
@app.route('/UPLOAD_FILE', methods=['POST'])
def UPLOAD_FILE():
    import support.config
    from files.classify import classify_file
    from support.extension import ALLOWED_EXTENSIONS, retrieve_extension
    from support.generate import generate_code
        
    file = request.files.get('file')
    if not file:
            return jsonify({'success': False, 'message': 'No file detected.'}), 400
        
    exte = retrieve_extension(file.filename)
    if exte in ALLOWED_EXTENSIONS:
        code = generate_code(file.filename)
        filetype = classify_file(file.filename)

        match filetype:
            case "journal":
                from files.journals import extract_journals
                extracted = extract_journals(file, exte)
            case "customer":
                from files.customers import extract_customers
                extracted = extract_customers(file, exte)
            case "vendor":
                from files.vendors import extract_vendors
                extracted = extract_vendors(file, exte)
            case "account":
                from files.accounts import extract_accounts
                extracted = extract_accounts(file, exte)
            case _:
                pass

        if extracted is not None:
            print(f"CHECKPOINT: File Code {code} processed successfully")
            support.config.files[code] = {'name': file.filename, 'type': filetype, 'uploaded': False, 'df': extracted}
            return jsonify({'success': True, 'message': 'File upload success of type {filetype}.'}), 200

    print(f"WARNING: File was not processed or other data validation error")
    return jsonify({'success': False, 'message': 'Invalid file extension or processing error.'}), 400

# send customers over to QBD
@app.route('/POST_CUSTOMERS', methods=['POST'])
def POST_CUSTOMERS():
    import support.config
    from api.objects import post_objects
    result = post_objects(
        files=support.config.files, 
        object_mode="customer")

    if result:
        return jsonify({'success': True, 'message': 'Posting Customers success.'}), 200

    return jsonify({'success': False, 'message': 'Posting Customers failure.'}), 400

# send invoices over to QBD
@app.route('/POST_INVOICES', methods=['POST'])
def POST_INVOICES():
    import support.config
    from api.items import post_items
    result = post_items(
        files=support.config.files, 
        begin_date=support.config.begin_date, 
        end_date=support.config.end_date,
        item_mode="invoice")

    if result:
        return jsonify({'success': True, 'message': 'Posting Invoices success.'}), 200
        
    return jsonify({'success': False, 'message': 'Posting Invoices failed.'}), 400

# send vendors over to QBD
@app.route('/POST_VENDORS', methods=['POST'])
def POST_VENDORS():
    import support.config
    from api.objects import post_objects
    result = post_objects(
        files=support.config.files, 
        object_mode="vendor")

    if result:
        return jsonify({'success': True, 'message': 'Posting Vendors success.'}), 200

    return jsonify({'success': False, 'message': 'Posting Vendors failure.'}), 400

# send bills over to QBD
@app.route('/POST_BILLS', methods=['POST'])
def POST_BILLS():
    import support.config
    from api.items import post_items
    result = post_items(
        files=support.config.files, 
        begin_date=support.config.begin_date, 
        end_date=support.config.end_date,
        item_mode="bill")

    if result:
        return jsonify({'success': True, 'message': 'Posting Bills success.'}), 200
        
    return jsonify({'success': False, 'message': 'Posting Bills failed.'}), 400

@app.route('/POST_ACCOUNTS', methods=['POST'])
def POST_ACCOUNTS():
    import support.config
    from api.objects import post_objects
    result = post_objects(
        files=support.config.files, 
        object_mode="account")
    
    if result:
        return jsonify({'success': True, 'message': 'Posting Accounts success'}), 200
    
    return jsonify({'success': False, 'message': 'Posting Accounts failed.'}), 400

@app.route('/POST_BANKS', methods=['POST'])
def POST_BANKS():
    import support.config
    result = True

    if result:
        return jsonify({'success': True, 'message': 'Post Banks success.'}), 200
    
    return jsonify({'success': False, 'message': 'Post Banks failure.'}), 400

    

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: python3 app.py")
        sys.exit(1)

    # TODO(prod): Do not rely on ngrok in production; remove hardcoded domain. Use reverse proxy/ingress with TLS.
    # TODO(prod): Fail fast if required env vars missing; do not print secrets; use proper logger.
    # TODO(prod): Serve on 0.0.0.0 and port from env in containerized envs.

    # global variable for mode and dates (dropdown changeable)
    import support.config
    support.config.env_mode = "sandbox"
    support.config.begin_date = "2025-01-01"
    support.config.end_date = "2025-01-31"

    # ngrok tunnel URL (will be set when tunnel is created)
    ngrok_url = None

    # Check if ngrok is available and create tunnel
    import importlib.util
    ngrok_spec = importlib.util.find_spec("ngrok")
    # TODO(prod): Only enable ngrok in local dev; guard under ENV_MODE == 'dev'.
    
    # Authenticate with ngrok using environment token
    if ngrok_token is None:
        print("ERROR: Please set your ngrok token")  # TODO(prod): local dev only; remove in prod.
        sys.exit(1)

    # Authenticate with ngrok using environment token
    if ngrok_token is None:
        print("ERROR: Please set your ngrok token")
        sys.exit(1)
    
    from ngrok import set_auth_token
    set_auth_token(ngrok_token)

    from ngrok import connect
    tunnel = connect(5000, domain="guiding-needlessly-mallard.ngrok-free.app")  # TODO(prod): remove hardcoded domain; config/env.

    # Collect quickbooks online token and account number
    # TODO(prod): Use QBO_CLIENT_ID/SECRET and QBO_REDIRECT_URI; do not store dynamic tokens in env.

    if tunnel is None:
        print("ERROR: Failed to connect to ngrok tunnel, check active instances")
        sys.exit(1)

    print("##############################_APP_BEGIN_##############################")

    # Static domain is configured in api/connect.py
    print(f"CHECKPOINT: Using static domain: https://guiding-needlessly-mallard.ngrok-free.app/oauth/callback")

    # Collect quickbooks online token and account number
    support.config.qbo_token = os.environ.get('QBO_PROD_TOKEN') if support.config.env_mode == "production" else os.environ.get('QBO_DEV_TOKEN')
    support.config.qbo_account = os.environ.get('QBO_PROD_ACCOUNT') if support.config.env_mode == "production" else os.environ.get('QBO_DEV_ACCOUNT')
   
    if support.config.qbo_token is None or support.config.qbo_account is None:
        print("ERROR: Please set both your QBO token and account number in environment")
        sys.exit(1)

    # dictionary for uploaded files
    support.config.files = {}

    # Validate global variables are properly set
    print(f"CHECKPOINT: Environment mode set to: {support.config.env_mode}")
    print(f"CHECKPOINT: QBO Token configured: {'Yes' if support.config.qbo_token else 'No'}")
    print(f"CHECKPOINT: QBO Account configured: {'Yes' if support.config.qbo_account else 'No'}")
    print(f"CHECKPOINT: Files dictionary initialized: {'Yes' if support.config.files is not None else 'No'}")
    print(f"CHECKPOINT: Date range set: {support.config.begin_date} to {support.config.end_date}")

    print("##############################_APP_END_##############################")
    # run the app on port 5000
    app.run(port=5000)
