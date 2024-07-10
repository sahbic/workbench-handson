import os
import sys
import json
import requests
from sasctl import Session

SERVER = "https://create.demo.sas.com/"

def _generate_access_token(refresh_file, verification=False):
    # get access token for viya env using refresh token.
    server = SERVER
    url = f"{server}/SASLogon/oauth/token"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic c2FzLmNsaTo='
    }

    # reading long-lived refresh token from txt file
    with open('refresh_token.txt', 'r') as token:
        refresh_token = token.read()

    refresh_payload = f'grant_type=refresh_token&refresh_token={refresh_token}'

    # response = requests.request("POST", url, headers=headers, data=refresh_payload, verify=False)
    response = requests.request("POST", url, headers=headers, data=refresh_payload, verify=verification)
    access_token = response.json()['access_token']
    return access_token

def _generate_tokens(auth_code, verification=False):
    server = SERVER
    url = f"{server}/SASLogon/oauth/token"

    # Payload and headers for the request
    auth_payload = f'grant_type=authorization_code&code={auth_code}'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic c2FzLmNsaTo='
    }
	
    response = requests.request("POST", url, headers=headers, data=auth_payload, verify=verification)
    response_json = json.loads(response.text)
	
    # Extract the access and the refresh tokens from the response
    access_token = response_json['access_token']
    refresh_token = response_json['refresh_token']
	
    # Save the refresh token to a .txt file:
    with open('refresh_token.txt', 'w') as file:
        file.write(refresh_token)
    return access_token, refresh_token

def get_connection(verification=None, refresh_file=None):
    if refresh_file is None:
        auth_code = input('Please provide your access token by going to https://create.demo.sas.com/SASLogon/oauth/authorize?client_id=sas.cli&response_type=code:')
        access_token, refresh_token = _generate_tokens(auth_code, verification=verification)
        with open('refresh_token.txt', 'w') as file:
            file.write(refresh_token)
    else:
        access_token = _generate_access_token(refresh_file, verification=verification)

    if not verification:
        st = Session(SERVER, token=access_token, verify_ssl=False)
        print(f'Connection established: {st}')
    else:
        os.environ['CAS_CLIENT_SSL_CA_LIST'] = verification
        st = Session(SERVER, token=access_token)
        print(f'Connection established: {st}')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        get_connection()
    elif len(sys.argv) == 2:
        refresh_file = sys.argv[1]
        get_connection(refresh_file=refresh_file)
    elif len(sys.argv) == 3:
        refresh_file = sys.argv[1]
        verification_file = sys.argv[2]
        print(f"refresh_file received: {refresh_file}")
        print(f"verification_file received: {verification_file}")
        get_connection(verification=verification_file, refresh_file=refresh_file)
