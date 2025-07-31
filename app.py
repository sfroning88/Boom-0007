import os, sys
from flask import Flask, render_template, request, jsonify

# create a Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# get Quickbooks Online token
qbo_token = os.environ.get('QBO_API_KEY')

# get Quickbooks Online account
qbo_account = os.environ.get('QBO_ACCOUNT_NUMBER')

@app.route('/')
def home():
    return render_template('chat.html')

# generic button function
@app.route('/BUTTON_FUNCTION_ONE', methods=['POST'])
def BUTTON_FUNCTION_ONE():
    try:
        return jsonify({'success': True, 'message': 'Button Function One success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# generic button function
@app.route('/BUTTON_FUNCTION_TWO', methods=['POST'])
def BUTTON_FUNCTION_TWO():
    try:
        return jsonify({'success': True, 'message': 'Button Function Two success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/BUTTON_FUNCTION_THREE', methods=['POST'])
def BUTTON_FUNCTION_THREE():
    try:
        return jsonify({'success': True, 'message': 'Button Function Three success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/BUTTON_FUNCTION_FOUR', methods=['POST'])
def BUTTON_FUNCTION_FOUR():
    try:
        return jsonify({'success': True, 'message': 'Button Function Four success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/BUTTON_FUNCTION_FIVE', methods=['POST'])
def BUTTON_FUNCTION_FIVE():
    try:
        return jsonify({'success': True, 'message': 'Button Function Five success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/BUTTON_FUNCTION_SIX', methods=['POST'])
def BUTTON_FUNCTION_SIX():
    try:
        return jsonify({'success': True, 'message': 'Button Function Six success.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

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
