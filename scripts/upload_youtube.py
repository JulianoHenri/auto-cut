#!/usr/bin/env python3
import os
import argparse

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_service():
client_id = os.environ.get("YT_CLIENT_ID")
client_secret = os.environ.get("YT_CLIENT_SECRET")
refresh_token = os.environ.get("YT_REFRESH_TOKEN")

if not client_id or not client_secret or not refresh_token:
    raise SystemExit("Faltam env vars: YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN")

creds = Credentials(
    token=None,
    refresh_token=refresh_token,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=client_id,
    client_secret=client_secret,
    scopes=SCOPES,
)

return build("youtube", "v3", credentials=creds)
def main():
p = argparse.ArgumentParser()
p.add_argument("--file", required=True, help="Path do mp4")
p.add_argument("--title", required=True)
p.add_argument("--description", default="")
p.add_argument("--privacy", default="unlisted", choices=["unlisted","public","private"])
p.add_argument("--tags", default="", help="CSV opcional: tag1,tag2")
p.add_argument("--categoryId", default="22") # 22 = People & Blogs (ajuste se quiser)
args = p.parse_args()

youtube = get_service()

body = {
    "snippet": {
        "title": args.title[:100],
        "description": args.description,
        "categoryId": args.categoryId,
    },
    "status": {
        "privacyStatus": args.privacy
    }
}

if args.tags.strip():
    body["snippet"]["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]

media = MediaFileUpload(args.file, mimetype="video/mp4", resumable=True)

req = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)

resp = None
while resp is None:
    status, resp = req.next_chunk()

# Retorna ID do vídeo
print(resp.get("id"))
if name == "main":
main()