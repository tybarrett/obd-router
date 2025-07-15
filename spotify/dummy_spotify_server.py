"""dummy_spotify_server.py - run this to receive redirect requests and print out the URL params."""

from flask import Flask, send_file, request, redirect
import json

app = Flask(__name__)

@app.route("/")
def index():
    print(f"{request.args.to_dict()=}")
    return {}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
