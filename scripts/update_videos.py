"""Update README.md with latest YouTube videos as a thumbnail grid."""
from __future__ import annotations

import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCDT8sIFy3pW8LT6SAbe8xtQ"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
MAX_VIDEOS = 6
COLS = 3
README = Path("README.md")
START = "<!-- YOUTUBE-VIDEOS:START -->"
END = "<!-- YOUTUBE-VIDEOS:END -->"

NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def fetch_videos():
    with urllib.request.urlopen(FEED, timeout=30) as r:
        root = ET.fromstring(r.read())
    out = []
    for entry in root.findall("a:entry", NS)[:MAX_VIDEOS]:
        vid = entry.find("yt:videoId", NS).text
        title = entry.find("a:title", NS).text
        out.append((vid, title))
    return out


def build_block(videos):
    cells = []
    for vid, title in videos:
        thumb = f"https://img.youtube.com/vi/{vid}/mqdefault.jpg"
        url = f"https://www.youtube.com/watch?v={vid}"
        safe_title = title.replace("|", "&#124;")
        cells.append(
            f'<td width="33%" valign="top" align="center">'
            f'<a href="{url}"><img src="{thumb}" width="320" alt=""/></a><br/>'
            f'<a href="{url}"><b>{safe_title}</b></a></td>'
        )

    rows = []
    for i in range(0, len(cells), COLS):
        rows.append("<tr>" + "".join(cells[i : i + COLS]) + "</tr>")

    return f"{START}\n<table>\n" + "\n".join(rows) + f"\n</table>\n{END}"


def main():
    videos = fetch_videos()
    if not videos:
        return
    block = build_block(videos)
    text = README.read_text()
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if new != text:
        README.write_text(new)
        print(f"Updated with {len(videos)} videos.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
