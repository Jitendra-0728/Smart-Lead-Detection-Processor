
# Step 1 - Task 1.3 Test Zoho CRM Connection - Completed

from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuration - Replace with your actual values
ZOHO_CONFIG = {
    'client_id': '1000.IVI7THPC35ZS5DKKK1UXX8KXPET28B840H',  # Replace with your actual client ID
    'client_secret': 'f2dfe500a17e6a050a5b3e48b7dc56ab40466acef4',  # Replace with your actual client secret
    'redirect_uri': 'http://localhost:5000/zoho/callback',  # Update this based on your setup
    'scope': 'ZohoCRM.modules.ALL,ZohoCRM.users.READ',
    'access_type': 'offline'
}

# File to store tokens
TOKENS_FILE = '../tokens.json'


def save_tokens(token_data):
    """Save tokens to a JSON file"""
    with open(TOKENS_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    print(f"Tokens saved to {TOKENS_FILE}")


def load_tokens():
    """Load tokens from JSON file"""
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    return None


def refresh_access_token():
    """Refresh the access token using refresh token"""
    tokens = load_tokens()
    if not tokens or 'refresh_token' not in tokens:
        return None

    payload = {
        'refresh_token': tokens['refresh_token'],
        'client_id': ZOHO_CONFIG['client_id'],
        'client_secret': ZOHO_CONFIG['client_secret'],
        'grant_type': 'refresh_token'
    }

    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=payload)
        if response.status_code == 200:
            new_tokens = response.json()
            # Keep the refresh token from the old tokens
            new_tokens['refresh_token'] = tokens['refresh_token']
            save_tokens(new_tokens)
            return new_tokens
        else:
            print(f"Token refresh failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return None


@app.route('/')
def home():
    """Home page with authorization link"""
    auth_url = (
        f"https://accounts.zoho.com/oauth/v2/auth?"
        f"scope={ZOHO_CONFIG['scope']}&"
        f"client_id={ZOHO_CONFIG['client_id']}&"
        f"response_type=code&"
        f"access_type={ZOHO_CONFIG['access_type']}&"
        f"redirect_uri={ZOHO_CONFIG['redirect_uri']}"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Zoho CRM Integration</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .success {{ color: green; }}
            .error {{ color: red; }}
            .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Zoho CRM Integration Setup</h1>

            <div class="info">
                <h3>Step 1: Configure Zoho API Console</h3>
                <p>Make sure your Zoho API Console has this redirect URI configured:</p>
                <code>{ZOHO_CONFIG['redirect_uri']}</code>
            </div>

            <div class="info">
                <h3>Step 2: Authorize Application</h3>
                <p>Click the button below to authorize this application with Zoho:</p>
                <a href="{auth_url}" class="btn">Authorize with Zoho CRM</a>
            </div>

            <div class="info">
                <h3>Step 3: Test Integration</h3>
                <p>After authorization, you can:</p>
                <ul>
                    <li><a href="/zoho/status">Check Token Status</a></li>
                    <li><a href="/zoho/create_lead">Create Test Lead</a></li>
                    <li><a href="/zoho/get_leads">Get Leads</a></li>
                </ul>
            </div>

            <div class="info">
                <h3>Current Configuration:</h3>
                <ul>
                    <li><strong>Client ID:</strong> {ZOHO_CONFIG['client_id']}</li>
                    <li><strong>Redirect URI:</strong> {ZOHO_CONFIG['redirect_uri']}</li>
                    <li><strong>Scope:</strong> {ZOHO_CONFIG['scope']}</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/zoho/callback')
def zoho_callback():
    """Handle OAuth callback from Zoho"""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"<h1>Authorization Error</h1><p>{error}</p>", 400

    if not code:
        return "<h1>Error</h1><p>No authorization code received</p>", 400

    # Exchange code for tokens
    payload = {
        'grant_type': 'authorization_code',
        'client_id': ZOHO_CONFIG['client_id'],
        'client_secret': ZOHO_CONFIG['client_secret'],
        'redirect_uri': ZOHO_CONFIG['redirect_uri'],
        'code': code
    }

    try:
        response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=payload)

        if response.status_code == 200:
            tokens = response.json()
            tokens['obtained_at'] = datetime.now().isoformat()
            save_tokens(tokens)
            print(tokens)

            return f"""
            <h1>✅ Authorization Successful!</h1>
            <p>Access token obtained and saved.</p>
            <p><strong>Token expires in:</strong> {tokens.get('expires_in', 'Unknown')} seconds</p>
            <p><a href="/zoho/status">Check Token Status</a></p>
            <p><a href="/zoho/create_lead">Create Test Lead</a></p>
            <p><a href="/">Back to Home</a></p>
            """
        else:
            error_details = response.json() if response.headers.get(
                'content-type') == 'application/json' else response.text
            return f"""
            <h1>❌ Token Exchange Failed</h1>
            <p>Status Code: {response.status_code}</p>
            <p>Error: {error_details}</p>
            <p><a href="/">Try Again</a></p>
            """, 400

    except Exception as e:
        return f"""
        <h1>❌ Error</h1>
        <p>Exception occurred: {str(e)}</p>
        <p><a href="/">Try Again</a></p>
        """, 500


@app.route('/zoho/status')
def token_status():
    """Check current token status"""
    tokens = load_tokens()
    if not tokens:
        return "<h1>❌ No Tokens Found</h1><p><a href='/'>Authorize First</a></p>"

    html = f"""
    <h1>Token Status</h1>
    <ul>
        <li><strong>Access Token:</strong> {tokens.get('access_token', 'N/A')[:20]}...</li>
        <li><strong>Refresh Token:</strong> {tokens.get('refresh_token', 'N/A')[:20]}...</li>
        <li><strong>Expires In:</strong> {tokens.get('expires_in', 'N/A')} seconds</li>
        <li><strong>Obtained At:</strong> {tokens.get('obtained_at', 'N/A')}</li>
    </ul>
    <p><a href="/zoho/refresh_token">Refresh Token</a></p>
    <p><a href="/">Back to Home</a></p>
    """
    return html


@app.route('/zoho/refresh_token')
def refresh_token_route():
    """Refresh the access token"""
    new_tokens = refresh_access_token()
    if new_tokens:
        return "<h1>✅ Token Refreshed Successfully</h1><p><a href='/zoho/status'>Check Status</a></p>"
    else:
        return "<h1>❌ Token Refresh Failed</h1><p><a href='/'>Reauthorize</a></p>"


@app.route('/zoho/create_lead')
def create_lead():
    """Create a test lead in Zoho CRM"""
    tokens = load_tokens()
    if not tokens:
        return "<h1>❌ No Tokens Found</h1><p><a href='/'>Authorize First</a></p>"

    access_token = tokens.get('access_token')
    if not access_token:
        return "<h1>❌ No Access Token</h1><p><a href='/'>Authorize First</a></p>"

    # Sample lead data
    lead_data = {
        "data": [{
            "Last_Name": "Test Lead",
            "First_Name": "API",
            "Email": "test@perfectdataentry.com",
            "Company": "Perfect Data Entry",
            "Phone": "123-456-7890",
            "Lead_Source": "API Integration",
            "Lead_Status": "Not Contacted"
        }]
    }

    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://www.zohoapis.com/crm/v2/Leads',
            json=lead_data,
            headers=headers
        )

        if response.status_code == 201:
            result = response.json()
            return f"""
            <h1>✅ Lead Created Successfully!</h1>
            <p><strong>Lead ID:</strong> {result['data'][0]['details']['id']}</p>
            <p><strong>Response:</strong> {json.dumps(result, indent=2)}</p>
            <p><a href="/zoho/get_leads">View All Leads</a></p>
            <p><a href="/">Back to Home</a></p>
            """
        else:
            return f"""
            <h1>❌ Failed to Create Lead</h1>
            <p><strong>Status Code:</strong> {response.status_code}</p>
            <p><strong>Response:</strong> {response.text}</p>
            <p><a href="/zoho/refresh_token">Try Refreshing Token</a></p>
            <p><a href="/">Back to Home</a></p>
            """

    except Exception as e:
        return f"""
        <h1>❌ Error Creating Lead</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><a href="/">Back to Home</a></p>
        """


@app.route('/zoho/get_leads')
def get_leads():
    """Fetch leads from Zoho CRM"""
    tokens = load_tokens()
    if not tokens:
        return "<h1>❌ No Tokens Found</h1><p><a href='/'>Authorize First</a></p>"

    access_token = tokens.get('access_token')
    if not access_token:
        return "<h1>❌ No Access Token</h1><p><a href='/'>Authorize First</a></p>"

    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            'https://www.zohoapis.com/crm/v2/Leads?per_page=10',
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            leads = result.get('data', [])

            html = "<h1>📋 Recent Leads</h1>"
            if leads:
                html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr><th>Name</th><th>Email</th><th>Company</th><th>Phone</th><th>Status</th></tr>"

                for lead in leads[:10]:  # Show first 10 leads
                    html += f"""
                    <tr>
                        <td>{lead.get('First_Name', '')} {lead.get('Last_Name', '')}</td>
                        <td>{lead.get('Email', '')}</td>
                        <td>{lead.get('Company', '')}</td>
                        <td>{lead.get('Phone', '')}</td>
                        <td>{lead.get('Lead_Status', '')}</td>
                    </tr>
                    """
                html += "</table>"
            else:
                html += "<p>No leads found.</p>"

            html += "<p><a href='/zoho/create_lead'>Create Test Lead</a></p>"
            html += "<p><a href='/'>Back to Home</a></p>"

            return html
        else:
            return f"""
            <h1>❌ Failed to Fetch Leads</h1>
            <p><strong>Status Code:</strong> {response.status_code}</p>
            <p><strong>Response:</strong> {response.text}</p>
            <p><a href="/zoho/refresh_token">Try Refreshing Token</a></p>
            <p><a href="/">Back to Home</a></p>
            """

    except Exception as e:
        return f"""
        <h1>❌ Error Fetching Leads</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><a href="/">Back to Home</a></p>
        """


if __name__ == '__main__':
    print("🚀 Starting Zoho CRM Integration Server...")
    print("📋 Make sure to update the following in your Zoho API Console:")
    print(f"   Redirect URI: {ZOHO_CONFIG['redirect_uri']}")
    print(f"   Client Secret: Update the CLIENT_SECRET in the code")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔗 Authorization URL will be shown on the home page")

    app.run(debug=True, host='0.0.0.0', port=5000)
