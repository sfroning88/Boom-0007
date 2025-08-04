import os, sys
from flask import Flask, render_template, jsonify, request

# create a Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# get Quickbooks Online token
qbo_token = os.environ.get('QBO_API_KEY')

# get Quickbooks Online account
qbo_account = os.environ.get('QBO_ACCOUNT_NUMBER')

# dictionary for uploaded files
files = {}

@app.route('/')
def home():
    return render_template('chat.html')

# connecting first time to qbo for authorization
@app.route('/CONNECT_QBO', methods=['POST'])
def CONNECT_QBO():
    # Generate OAuth URL for user to authorize once
    from api.connect import get_oauth_url
    oauth_url = get_oauth_url(qbo_token, qbo_account)
        
    if oauth_url:
        return jsonify({'success': True, 'message': 'Redirecting to QBO authorization...', 'redirect_url': oauth_url}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to generate OAuth URL'}), 400

@app.route('/oauth/callback')
def oauth_callback():
    auth_code = request.args.get('code')
    realm_id = request.args.get('realmId')
        
    if not auth_code or not realm_id:
        return jsonify({'success': False, 'message': 'Missing authorization code or realm ID'}), 400
        
    # Connect to QBO with the received auth code and store refresh token
    from api.connect import connect_qbo
    success = connect_qbo(qbo_token, qbo_account, auth_code, realm_id)
        
    if success:
        # Show success page that will update the main app
        return render_template('oauth_success.html', message='QBO connection established successfully!')
    else:
        return render_template('oauth_error.html', message='Failed to establish QBO connection')

# uploading different QBD files
@app.route('/UPLOAD_FILE', methods=['POST'])
def UPLOAD_FILE():
    from functions.extension import ALLOWED_EXTENSIONS, retrieve_extension
    from functions.generate import generate_code
    from functions.classify import classify_file
        
    file = request.files.get('file')
    if not file:
            return jsonify({'success': False, 'message': 'No file detected.'}), 400
        
    exte = retrieve_extension(file.filename)
    if exte in ALLOWED_EXTENSIONS:
        code = generate_code(file.filename)
        filetype = classify_file(file.filename)

        match filetype:
            case "journal":
                from functions.journals import extract_journals
                extracted = extract_journals(file, exte)
            case "customer":
                from functions.customers import extract_customers
                extracted = extract_customers(file, exte)
            case "vendor":
                from functions.vendors import extract_vendors
                extracted = extract_vendors(file, exte)
            case _:
                pass

        print(f"File Code {code} processed successfully.")
        files[code] = {'name': file.filename, 'type': filetype, 'uploaded': False, 'df': extracted}

        return jsonify({'success': True, 'message': 'File upload success of type {filetype}.'}), 200

    return jsonify({'success': False, 'message': 'Invalid file extension.'}), 400

# send customers over to QBD
@app.route('/POST_CUSTOMERS', methods=['POST'])
def POST_CUSTOMERS():
    from api.customers import post_customers
    result = post_customers(files)

    if result:
        return jsonify({'success': True, 'message': 'Posting Customers success.'}), 200

    return jsonify({'success': False, 'message': 'Posting Customers failure.'}), 400

# send invoices over to QBD
@app.route('/POST_INVOICES', methods=['POST'])
def POST_INVOICES():
    from api.invoices import post_invoices
    result = post_invoices(files)

    if result:
        return jsonify({'success': True, 'message': 'Posting Invoices success.'}), 200
        
    return jsonify({'success': False, 'message': 'Posting Invoices failed.'}), 400

# send vendors over to QBD
@app.route('/POST_VENDORS', methods=['POST'])
def POST_VENDORS():
    from api.vendors import post_vendors
    result = post_vendors(files)

    if result:
        return jsonify({'success': True, 'message': 'Posting Vendors success.'}), 200

    return jsonify({'success': False, 'message': 'Posting Vendors failure.'}), 400

# send bills over to QBD
@app.route('/POST_BILLS', methods=['POST'])
def POST_BILLS():
    from api.bills import post_bills
    result = post_bills(files)

    if result:
        return jsonify({'success': True, 'message': 'Posting Bills success.'}), 200
        
    return jsonify({'success': False, 'message': 'Posting Bills failed.'}), 400

@app.route('/BUTTON_FUNCTION_SEVEN', methods=['POST'])
def BUTTON_FUNCTION_SEVEN():
    try:
        return jsonify({'success': True, 'message': 'Button Function Seven success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/BUTTON_FUNCTION_EIGHT', methods=['POST'])
def BUTTON_FUNCTION_EIGHT():
    try:
        return jsonify({'success': True, 'message': 'Button Function Eight success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: python3 app.py")
        sys.exit(1)

    # run the app
    app.run(debug=True, port=5000)
