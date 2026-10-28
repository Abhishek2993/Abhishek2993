import html
import re
import textwrap
import urllib.request
import xml.etree.ElementTree as ET

WIDTH = 27
README_PATH = "README.md"
START_MARKER = "<!-- NEWS-TICKER:START -->"
END_MARKER = "<!-- NEWS-TICKER:END -->"
FEED_URL = "https://techcrunch.com/feed/"
USER_AGENT = "Mozilla/5.0 (compatible; profile-readme-news-ticker/1.0)"


def fetch_headlines(n=4, max_len=90):
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        xml_bytes = resp.read()

    root = ET.fromstring(xml_bytes)
    headlines = []
    for item in root.iter("item"):
        title_el = item.find("title")
        if title_el is None or not title_el.text:
            continue
        title = html.unescape(title_el.text.strip())
        title = textwrap.shorten(title, width=max_len, placeholder="…")
        headlines.append(title)
        if len(headlines) >= n:
            break
    return headlines


def build_tv(headlines):
    lines = []
    for h in headlines:
        lines.extend(textwrap.wrap(f"* {h}", width=WIDTH))

    top = "┌" + "─" * (WIDTH + 2) + "┐"
    bottom = "└" + "─" * (WIDTH + 2) + "┘"
    header = "│ " + "ON AIR - TECH NEWS".center(WIDTH) + " │"
    sep = "│ " + "─" * WIDTH + " │"
    body = ["│ " + l.ljust(WIDTH) + " │" for l in lines]

    box_width = len(top)
    antenna = " " * (box_width // 2 - 1) + "\\  /"
    stand = " " * ((box_width - 10) // 2) + "[___]___[___]"

    art = [antenna, top, header, sep, *body, bottom, stand]
    return "```\n" + "\n".join(art) + "\n```"


def main():
    headlines = fetch_headlines()
    if not headlines:
        return

    tv = build_tv(headlines)

    with open(README_PATH, encoding="utf-8") as f:
        readme = f.read()

    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    replacement = f"{START_MARKER}\n{tv}\n{END_MARKER}"
    new_readme, count = pattern.subn(replacement, readme)

    if count and new_readme != readme:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_readme)


if __name__ == "__main__":
    main()
