import os
import glob
from bs4 import BeautifulSoup
from datetime import datetime

SITE_URL = "https://www.peterfarrarbooks.com"
BLOG_DIR = "blog"
OUTPUT = "feed.xml"

posts = []

for filepath in glob.glob(f"{BLOG_DIR}/**/*.html", recursive=True):
    if "index" in filepath or "post-template" in filepath:
        continue
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    def og(prop):
        tag = soup.find("meta", property=f"og:{prop}")
        return tag["content"] if tag else ""

    def meta(name):
        tag = soup.find("meta", attrs={"name": name})
        return tag["content"] if tag else ""

    schema = soup.find("script", {"type": "application/ld+json"})
    date_published = ""
    category = ""
    if schema:
        import json
        try:
            data = json.loads(schema.string)
            if isinstance(data, list):
                for d in data:
                    if d.get("@type") == "BlogPosting":
                        date_published = d.get("datePublished", "")
                        category = d.get("articleSection", "")
            elif data.get("@type") == "BlogPosting":
                date_published = data.get("datePublished", "")
                category = data.get("articleSection", "")
        except:
            pass

    slug = filepath.replace("\\", "/").replace(f"{BLOG_DIR}/", "").replace(".html", "")
    url = f"{SITE_URL}/blog/{slug}/"

    posts.append({
        "title": og("title") or soup.title.string or "",
        "url": og("url") or url,
        "description": og("description") or meta("description") or "",
        "image": og("image"),
        "date": date_published,
        "category": category,
    })

# Sort newest first
posts.sort(key=lambda x: x["date"], reverse=True)

def to_rfc822(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%a, %d %b %Y 09:00:00 +0000")
    except:
        return ""

items = ""
for p in posts:
    items += f"""
    <item>
      <title><![CDATA[{p['title']}]]></title>
      <link>{p['url']}</link>
      <guid>{p['url']}</guid>
      <pubDate>{to_rfc822(p['date'])}</pubDate>
      <description><![CDATA[{p['description']}]]></description>
      <category>{p['category']}</category>
      <enclosure url="{p['image']}" length="0" type="image/jpeg"/>
    </item>"""

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Peter Farrar Books — Blog</title>
    <link>{SITE_URL}/blog/</link>
    <description>Photography insights, leadership thinking, and updates on new books and projects.</description>
    <language>en-gb</language>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    {items}
  </channel>
</rss>"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(feed)

print(f"Feed generated with {len(posts)} posts.")
