from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask_session import Session
import requests
from dotenv import load_dotenv
dotenv_path = 'E:/VSC FILES/AMZN SHIPPING WEBAPP/cred.env'
load_dotenv(dotenv_path=dotenv_path)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_very_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to obtain UPS OAuth2 access token
def get_ups_access_token():
    token_url = 'https://wwwcie.ups.com/security/v1/oauth/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(token_url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    if response.status_code == 200:
        access_token = response.json()['access_token']
    
        return access_token
    else:
        print(f"Failed to obtain access token, status code: {response.status_code}, response: {response.text}")  # Adding detailed error logging
        return None

# Function to get delivery status from UPS
def get_delivery_status(tracking_number, access_token):
    api_url = f'https://onlinetools.ups.com/api/track/v1/details/{tracking_number}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'transId': 'UniqueTransId',
        'transactionSrc': 'testing',
    }
    print(f"Making API Request to: {api_url}")
    print("Headers:", headers)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        tracking_info = response.json()
        print(f"API Request Failed with status code: {response.status_code}")
        print("Response:", response.text)
        
        # Extract the package section
        packages = tracking_info.get("trackResponse", {}).get("shipment", [{}])[0].get("package", [])
        if not packages:
            return "No package information available"

        package = packages[0]  # Assuming we're only dealing with single-package shipments for simplicity

        # Extract delivery information
        delivery_date = package.get("deliveryDate", [{}])[0].get("date", "Date not available")
        delivery_time = package.get("deliveryTime", {}).get("endTime", "Time not available")

        # Format the delivery date and time
        formatted_delivery_date = f"{delivery_date[:4]}-{delivery_date[4:6]}-{delivery_date[6:]}"
        formatted_delivery_time = f"{delivery_time[:2]}:{delivery_time[2:4]}"

        # Extract the latest activity for additional status
        latest_activity = package.get("activity", [{}])[0]
        activity_description = latest_activity.get("status", {}).get("description", "Latest activity description not available")

        # Check if the package is delivered
        if latest_activity.get("status", {}).get("type") == "D":
            return f"{activity_description} on {formatted_delivery_date} at {formatted_delivery_time}."
        else:
            return f"Latest status: {activity_description} on {formatted_delivery_date} at {formatted_delivery_time}"
    else:
        return f"Error: {response.status_code}, {response.text}"

    

@app.route('/')
def index():
    session.clear()  # Clear session for a fresh start
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    category = request.form.get('category')
    files = request.files.getlist('file')
    file_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_paths.append(filepath)
    session[category] = file_paths
    print(f"Uploaded files for {category}: {session[category]}")  # Confirm paths are stored
    return jsonify({'message': f'{len(files)} files uploaded successfully.', 'paths': file_paths})

def make_tracking_link(tracking_number):
    return f'<a href="https://www.ups.com/track?loc=en_US&tracknum={tracking_number}" target="_blank">{tracking_number}</a>'

# Assuming get_ups_access_token and get_delivery_status functions are defined here...

@app.route('/confirm', methods=['GET'])
def confirm_and_process():
    try:
        if 'orders' not in session or 'tracking' not in session:
            return jsonify({'error': 'No files uploaded'}), 400

        orders_path = session['orders'][0]
        tracking_path = session['tracking'][0]

        orders_df = pd.read_csv(orders_path).astype(str)
        tracking_df = pd.read_csv(tracking_path).astype(str)

        # Renaming columns
        tracking_df.rename(columns={'Tracking': 'tracking-number', 'ToName': 'recipient-name'}, inplace=True)

        # Debugging: Print columns after renaming to confirm
        print(f"Tracking DF Columns after renaming: {tracking_df.columns.tolist()}")

        # Merge DataFrames
        combined_df = pd.merge(orders_df, tracking_df, how='left', on=['recipient-name', 'tracking-number'])

        # Confirm 'tracking-number' exists after merge
        if 'tracking-number' not in combined_df.columns:
            print("Error: 'tracking-number' column not found after merging.")
            return jsonify({'error': "Column 'tracking-number' not found after merging."}), 500
        
        # Continue with processing combined_df as before
        # ...

    except Exception as e:
        app.logger.error(f"Error processing files: {str(e)}")
        return jsonify({'error': f'Failed to process files: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')