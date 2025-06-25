#!/bin/bash

# Create the .streamlit directory if it doesn't exist
mkdir -p /app/.streamlit

# Generate secret.toml
cat <<EOF > /app/.streamlit/secret.toml
[general]
club='${CLUB}'
blob_connection_string='${BLOB_CONNECTION_STRING}'

[auth]
redirect_uri='${REDIRECT_URI}'
cookie_secret='${COOKIE_SECRET}'

[auth.auth0]
domain='${AUTH0_DOMAIN}'
client_id='${AUTH0_CLIENT_ID}'
client_secret='${AUTH0_CLIENT_SECRET}'
server_metadata_url='${AUTH0_METADATA_URL}'
EOF

# Start Streamlit
exec "$@"
