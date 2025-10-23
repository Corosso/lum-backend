def create_auth0_user(email, password=None, full_name=None, phone=None, is_verified=False, can_sell=False):
    """
    Crea un usuario en Auth0 y retorna el objeto de usuario creado.
    El password es opcional (Auth0 puede enviar email de invitación si no se provee).
    """
    token = get_auth0_token()
    url = f"https://{auth0_domain}/api/v2/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "connection": "Username-Password-Authentication",  # Cambia si usas otra conexión
        "email": email,
        "email_verified": is_verified,
        "user_metadata": {
            "numero": phone,
            "is_verified": is_verified,
            "can_sell": can_sell,
            "full_name": full_name
        }
    }
    if password:
        payload["password"] = password
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
import requests
import os

auth0_domain = os.getenv("AUTH0_DOMAIN")
auth0_client_id = os.getenv("AUTH0_CLIENT_ID")
auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET")
auth0_audience = os.getenv("AUTH0_AUDIENCE")

def get_auth0_token():
    url = f"https://{auth0_domain}/oauth/token"
    payload = {
        "client_id": auth0_client_id,
        "client_secret": auth0_client_secret,
        "audience": auth0_audience,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def update_auth0_user_metadata(auth0_user_id, metadata: dict):
    token = get_auth0_token()
    url = f"https://{auth0_domain}/api/v2/users/{auth0_user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_metadata": metadata
    }
    response = requests.patch(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
