"""get_refresh_token.py - runs Spotify's authorization code flow and saves a new refresh token."""

import datetime
import os
import secrets
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import dotenv
import requests


# Must exactly match a redirect URI registered in the Spotify developer dashboard.
REDIRECT_HOST = "127.0.0.1"
REDIRECT_PORT = 3000
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}"

SCOPES = "user-read-playback-state user-modify-playback-state"
REFRESH_TOKEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "refresh_token.txt")

# Spotify expires refresh tokens 6 months after the user authorizes.
REFRESH_TOKEN_LIFETIME = datetime.timedelta(days=182)


class _RedirectHandler(BaseHTTPRequestHandler):
    """Captures the query params Spotify sends back to REDIRECT_URI."""

    def do_GET(self):
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        if "code" not in query and "error" not in query:
            self.send_error(404)
            return

        self.server.params = query
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Spotify authorization received. You can close this tab.")

    def log_message(self, format, *args):
        pass


def wait_for_redirect():
    """Serve REDIRECT_URI until Spotify redirects the browser back, then return its query params."""
    server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), _RedirectHandler)
    server.params = None
    while server.params is None:
        server.handle_request()
    server.server_close()
    return server.params


def main():
    dotenv.load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set (e.g. in .env).")

    state = secrets.token_urlsafe(16)
    authorize_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    })
    print("Open this URL in a browser and approve access:\n\n" + authorize_url + "\n")
    print(f"Waiting for Spotify to redirect to {REDIRECT_URI} ...")

    params = wait_for_redirect()
    if params.get("state") != state:
        raise SystemExit("Redirect state did not match the request; aborting.")
    if "error" in params:
        raise SystemExit("Spotify authorization failed: " + params["error"])

    token_resp = requests.post("https://accounts.spotify.com/api/token",
                               auth=(client_id, client_secret),
                               data={"grant_type": "authorization_code",
                                     "code": params["code"],
                                     "redirect_uri": REDIRECT_URI,
                                     },
                               timeout=10)
    if not token_resp.ok:
        raise SystemExit(f"Token request failed ({token_resp.status_code}): {token_resp.text}")

    with open(REFRESH_TOKEN_PATH, "w") as refresh_token_fp:
        refresh_token_fp.write(token_resp.json()["refresh_token"])

    expires_on = datetime.date.today() + REFRESH_TOKEN_LIFETIME
    print(f"Saved new refresh token to {REFRESH_TOKEN_PATH}")
    print(f"It expires around {expires_on.isoformat()}.")


if __name__ == "__main__":
    main()
