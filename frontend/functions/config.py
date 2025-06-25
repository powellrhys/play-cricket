import os
from pathlib import Path

def generate_secrets_config_file():
    """
    """
    secrets_path = Path(".streamlit/secrets.toml")
    secrets_dir = secrets_path.parent

    if not secrets_path.exists():
        print("Creating missing secret.toml...")
        secrets_dir.mkdir(parents=True, exist_ok=True)

        content = f"""
            [general]
            club='{os.getenv("CLUB", "")}'
            blob_connection_string='{os.getenv("BLOB_CONNECTION_STRING", "")}'

            [auth]
            redirect_uri='{os.getenv("REDIRECT_URI", "")}'
            cookie_secret='{os.getenv("COOKIE_SECRET", "")}'

            [auth.auth0]
            domain='{os.getenv("AUTH0_DOMAIN", "")}'
            client_id='{os.getenv("AUTH0_CLIENT_ID", "")}'
            client_secret='{os.getenv("AUTH0_CLIENT_SECRET", "")}'
            server_metadata_url='{os.getenv("AUTH0_SERVER_METADATA_URL", "")}'
            """.strip()

        with open(secrets_path, "w") as f:
            f.write(content)
