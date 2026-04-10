"""
Generate secure environment variables for n8n and Supabase setup.
"""

import base64
import secrets
from datetime import datetime, timedelta
import jwt  # Make sure PyJWT is installed


def generate_jwt_token(secret, role):
    """Generate a JWT token for Supabase authentication.
    
    Args:
        secret (str): JWT secret key
        role (str): Role for the token (anon or service_role)
    
    Returns:
        str: JWT token
    """
    payload = {
        "role": role,
        "iss": "supabase",
        "iat": int(datetime.now().timestamp()),
        "exp": int((datetime.now() + timedelta(days=3650)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def generate_env_vars():
    """Generate environment variables.
    
    Returns:
        dict: Dictionary of generated environment variables
    """
    def generate_secure_key(bytes_length=32):
        return base64.urlsafe_b64encode(secrets.token_bytes(bytes_length)).decode('ascii').rstrip('=')
    
    # Generate Supabase specific keys
    jwt_secret = generate_secure_key(40)  # 40 chars as per Supabase docs
    postgres_password = generate_secure_key(32)
    dashboard_password = generate_secure_key(32)
    # Generate exactly 32 character hex string for vault_enc_key
    vault_enc_key = secrets.token_hex(16)  # 16 bytes = 32 hex characters
    secret_key_base = generate_secure_key(64)
    
    # Generate JWT tokens using the JWT secret
    anon_key = generate_jwt_token(jwt_secret, "anon")
    service_role_key = generate_jwt_token(jwt_secret, "service_role")
    
    # Generate n8n specific keys
    n8n_postgres_password = generate_secure_key(24)
    n8n_encryption_key = generate_secure_key(32)
    n8n_user_management_jwt_secret = generate_secure_key(48)
    
    # Create environment variables dictionary
    env_vars = {
        # Supabase variables
        "POSTGRES_PASSWORD": postgres_password,
        "JWT_SECRET": jwt_secret,
        "ANON_KEY": anon_key,
        "SERVICE_ROLE_KEY": service_role_key,
        "DASHBOARD_USERNAME": "supabase",  # Can be changed later
        "DASHBOARD_PASSWORD": dashboard_password,
        "SECRET_KEY_BASE": secret_key_base,
        "VAULT_ENC_KEY": vault_enc_key,
        
        # n8n variables
        "N8N_POSTGRES_PASSWORD": n8n_postgres_password,
        "N8N_ENCRYPTION_KEY": n8n_encryption_key,
        "N8N_USER_MANAGEMENT_JWT_SECRET": n8n_user_management_jwt_secret
    }
    print("Generated the following variables:")
    for key, value in env_vars.items():
        print(f"- {key}: {value}")
    
    return env_vars


if __name__ == "__main__":
    # Allow this file to be run directly for testing
    generate_env_vars() 