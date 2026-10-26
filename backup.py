"""Back up the playlists in this repository, in the same format as the backup
page in spotify-explore (src/js/components/Backup.tsx).

Usage: python3 backup.py

Signs in through spotify_player's cached login and only makes read-only GET
requests to the Spotify Web API. Writes the backup files next to this script.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# "liked" is the account's Liked Songs, which isn't a real playlist.
PLAYLISTS = {
    "69B0Fg4RltQUdC5JJKH11m": None,
    "liked": "Ben's Liked Songs",
    "6QAKnenuZoowNqxRzZbeRg": None,
    "5mhjf1Y4CSWX8i02vp0idf": None,
    "6G4aQ4pcQVKSR7KavEd5Sd": None,
    "5g6juK6pZSVQs8v8PFMX46": None,
    "7KYF90J2KSpfyPS2fQzxsg": None,
    "2t3V6Xyhc6rnZkjNG38itg": None,
}

CONFIG = os.path.expanduser("~/.config/spotify-player/app.toml")
CACHE = os.path.expanduser("~/.cache/spotify-player")

ALBUM_FILTER = "album(images,name,release_date,release_date_precision,genres,id)"
TRACK_FILTER = (
    "item(available_markets,is_playable,name,popularity,duration_ms,"
    f"linked_from,id,artists(name,genres,id,type),{ALBUM_FILTER})"
)
ITEMS_FILTER = f"items(added_at,{TRACK_FILTER})"
FIELD_FILTER = f"fields=snapshot_id,items(next,total,{ITEMS_FILTER})"


def access_token():
    # Any spotify_player command refreshes its cached token if it has expired.
    subprocess.run(["spotify_player", "get", "key", "devices"],
                   check=True, capture_output=True)
    client_id = re.search(r'^client_id\s*=\s*"([^"]+)"', open(CONFIG).read(), re.M)[1]
    with open(f"{CACHE}/{client_id}_token.json") as f:
        return json.load(f)["access_token"]


def api_get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en-US,en;q=0.9",
    })
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
            time.sleep(int(e.headers.get("Retry-After", 2 + attempt * 3)))
    raise RuntimeError(f"Gave up on {url}")


def to_track(t):
    return {
        "artist": ", ".join(a["name"] for a in t["artists"][:2]),
        "name": t["name"],
        "id": t["linked_from"]["id"] if t.get("linked_from") else t["id"],
    }


def fetch_playlist(playlist_id, token):
    base = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    info = api_get(f"{base}?fields=id,name", token)
    page = api_get(f"{base}?{FIELD_FILTER}&market=from_token", token)["items"]
    raw = page["items"]
    next_url = page["next"]
    while next_url:
        # Spotify's next URLs drop the fields filter, so put it back.
        parts = urllib.parse.urlsplit(next_url)
        query = dict(urllib.parse.parse_qsl(parts.query))
        query["fields"] = f"{ITEMS_FILTER},next"
        page = api_get(parts._replace(query=urllib.parse.urlencode(query)).geturl(), token)
        next_url = page.get("next")
        raw += page.get("items") or []
    return info, [to_track(item["item"]) for item in raw]


def fetch_liked(token, name):
    raw = []
    next_url = "https://api.spotify.com/v1/me/tracks?limit=50&market=from_token"
    while next_url:
        page = api_get(next_url, token)
        next_url = page.get("next")
        raw += page.get("items") or []
    tracks = [to_track(item.get("track") or item.get("item")) for item in raw]
    return {"id": "liked", "name": name}, tracks


def js_sort_key(s):
    # lodash sortBy compares with JS `<`, i.e. by UTF-16 code units.
    return s.lower().encode("utf-16-be")


def js_locale_now():
    # new Date().toLocaleString() in en-US: "8/12/2026, 4:57:20 PM"
    now = datetime.now()
    hour = now.hour % 12 or 12
    ampm = "AM" if now.hour < 12 else "PM"
    return f"{now.month}/{now.day}/{now.year}, {hour}:{now:%M:%S} {ampm}"


def write_backup(out_dir, info, tracks, generated):
    tracks = sorted(tracks, key=lambda t: js_sort_key(f"{t['artist']} - {t['name']}"))
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", info["name"])
    for suffix, label, line in [
        ("readable", "Artist - Song Name",
         lambda t: f"{t['artist']} - {t['name']}"),
        ("track-urls", "Spotify Track URLs",
         lambda t: f"https://open.spotify.com/track/{t['id']}"),
    ]:
        header = (
            "Spotify Playlist Backup\n"
            f"Playlist: {info['name']}\n"
            f"Playlist ID: {info['id']}\n"
            f"Generated on: {generated}\n"
            f"Total tracks: {len(tracks)}\n"
            f"Format: {label}\n\n"
        )
        path = os.path.join(out_dir, f"{safe_name}-backup-{suffix}.txt")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(header + "\n".join(line(t) for t in tracks))


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    token = access_token()
    generated = js_locale_now()
    for playlist_id, name in PLAYLISTS.items():
        if playlist_id == "liked":
            info, tracks = fetch_liked(token, name)
        else:
            info, tracks = fetch_playlist(playlist_id, token)
        if not tracks:
            print(f"No tracks found in playlist: {info['name']}", file=sys.stderr)
            continue
        write_backup(out_dir, info, tracks, generated)
        print(f"{info['name']}: {len(tracks)} tracks")


if __name__ == "__main__":
    main()
