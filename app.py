import boto3
import os
import json
import psycopg2
from flask import Flask, jsonify
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_db_credentials():
    secret_name = "my-app/db-credentials"  # Secret name in AWS Secrets Manager
    region_name = "us-east-1"  # Correct region for your secret, without the AZ suffix

    # Create a Secrets Manager client
    client = boto3.client(service_name="secretsmanager", region_name=region_name)

    # Fetch the secret value
    response = client.get_secret_value(SecretId=secret_name)

    secret = response['SecretString']
    secret_dict = json.loads(secret)

    # Ensure all necessary keys are present in the secret
    required_keys = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    for key in required_keys:
        if key not in secret_dict:
            raise KeyError(f"Missing expected key in secret: {key}")

    return secret_dict

def get_db_connection():
    creds = get_db_credentials()  # Fetch the credentials from Secrets Manager

    # Create a connection to the PostgreSQL database using the fetched credentials
    conn = psycopg2.connect(
        host=creds["DB_HOST"],  # Use the database host from the secret
        user=creds["DB_USER"],  # Use the database username from the secret
        password=creds["DB_PASSWORD"],  # Use the database password from the secret
        dbname=creds["DB_NAME"]  # Use the database name from the secret
    )
    return conn

@app.route('/status', methods=['GET'])
def status():
    try:
        conn = get_db_connection()  # Get the database connection
        cursor = conn.cursor()  # Create a cursor
        cursor.execute("SELECT 1")  # Test the connection by executing a simple query
        cursor.fetchall()  # Fetch the result
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection
        return jsonify({"status": "success", "message": "Connected to the database!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)


