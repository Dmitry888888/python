# download_photos_google_library.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import requests

# === CONFIGURATION ===
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
DOWNLOAD_DIR = 'T:/downloaded_photos_from_google_drive'
CREDENTIALS_FILE = 'credentials/credentials.json'
TOKEN_FILE = 'token.json'

FORCE_REAUTH = True  # Set to True to delete token and re-auth every time

if FORCE_REAUTH and os.path.exists(TOKEN_FILE):
    os.remove(TOKEN_FILE)
    print("🗑️ Deleted token.json for forced re-authentication")

# Use explicit discovery URL for Photos Library API
DISCOVERY_SERVICE_URL = 'https://photoslibrary.googleapis.com/$discovery/rest?version=v1'

# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_photos():
    """Download all photos from Google Photos using the Photos Library API."""
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        print(f"📎 Loading credentials from {TOKEN_FILE}")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Authenticate or refresh
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔁 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow — this may open your browser.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # Force consent to ensure correct scopes are granted
            creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')

        # Save new token with correct scopes
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        print(f"✅ Credentials saved to {TOKEN_FILE}")

    # Build the service using custom discovery URL
    print("🚀 Connecting to Google Photos Library API...")
    try:
        service = build('photoslibrary', 'v1', credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL)
    except Exception as e:
        print(f"❌ Failed to build service: {e}")
        print("💡 Make sure the Google Photos Library API is enabled at:")
        print("   https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com")
        return

    # Start downloading media items
    page_token = None
    count = 0
    skipped = 0

    print("📥 Fetching photos...")

    while True:
        try:
            results = service.mediaItems().list(
                pageSize=100,
                pageToken=page_token
            ).execute()
        except Exception as e:
            print(f"❌ Error fetching media items: {e}")
            break

        items = results.get('mediaItems', [])
        if not items:
            print("🎉 No more items found.")
            break

        for item in items:
            filename = item['filename']
            mime_type = item.get('mimeType', '').lower()

            # Support both images and videos
            if 'image' in mime_type or 'video' in mime_type:
                file_path = os.path.join(DOWNLOAD_DIR, filename)

                # Skip if already downloaded
                if os.path.exists(file_path):
                    skipped += 1
                    continue

                try:
                    # =d forces full quality download
                    url = item['baseUrl'] + '=d'
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()

                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    count += 1
                    print(f"[{count}] ✅ Downloaded: {filename} ({mime_type})")
                except Exception as e:
                    print(f"[⚠️] Failed to download {filename}: {e}")

            else:
                # Optional: log unsupported types
                pass

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    print(f"✅ All done! {count} new item(s) downloaded. {skipped} already existed.")


if __name__ == '__main__':
    download_photos()