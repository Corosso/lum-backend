from .auth0 import get_auth0_token
import os
import requests
from fastapi import HTTPException

def delete_auth0_user(auth0_user_id: str):
    """Elimina un usuario en Auth0 por su user_id."""
    auth0_domain = os.getenv("AUTH0_DOMAIN")
    token = get_auth0_token()
    url = f"https://{auth0_domain}/api/v2/users/{auth0_user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando usuario en Auth0: {e}")
