import os
from pathlib import Path
import hashlib

def generate_secrets_config_file():
    secrets_path = Path("/app/.streamlit/secret.toml")
    secrets_path.parent.mkdir(parents=True, exist_ok=True)

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
server_metadata_url='{os.getenv("AUTH0_METADATA_URL", "")}'
""".strip()

    content_hash = hashlib.sha256(content.encode()).hexdigest()

    if secrets_path.exists():
        current = secrets_path.read_text()
        current_hash = hashlib.sha256(current.encode()).hexdigest()
        if current_hash == content_hash:
            return  # No changes — do nothing

    with open(secrets_path, "w") as f:
        f.write(content)
