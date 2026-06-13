# Feed Formats Reference

## RSS 2.0

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Feed Title</title>
    <link>https://example.com</link>
    <description>Feed description</description>
    <item>
      <title>Item Title</title>
      <link>https://example.com/item</link>
      <description>Item description</description>
      <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
```

## Atom

```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Feed Title</title>
  <link href="https://example.com"/>
  <entry>
    <title>Entry Title</title>
    <link href="https://example.com/entry"/>
    <updated>2024-01-01T00:00:00Z</updated>
  </entry>
</feed>
```

## JSON Feed

```json
{
  "version": "https://jsonfeed.org/version/1",
  "title": "Feed Title",
  "items": [
    {
      "id": "1",
      "title": "Item Title",
      "content_text": "Item content",
      "url": "https://example.com/item"
    }
  ]
}
```
