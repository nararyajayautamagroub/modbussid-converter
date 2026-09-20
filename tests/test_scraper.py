from core.scraper import PageParser, _validate_url, crawl_site
from core.version import APP_VERSION


def test_scraper_parser_extracts_metadata():
    html = """
    <html>
      <head>
        <title>Example Page</title>
        <meta name="description" content="Example description">
        <meta property="og:title" content="OG Example">
        <link rel="canonical" href="https://example.com/canonical">
        <script type="application/ld+json">{"@type":"Thing","name":"Demo"}</script>
      </head>
      <body>
        <h1>Hello World</h1>
        <a href="/vehicle">Vehicle</a>
        <img src="/image.png">
        <p>Useful public content.</p>
      </body>
    </html>
    """
    parser = PageParser("https://example.com/", 20)
    parser.feed(html)

    assert parser.title_parts == ["Example Page"]
    assert parser.meta["description"] == "Example description"
    assert parser.meta["og:title"] == "OG Example"
    assert parser.canonical == "https://example.com/canonical"
    assert parser.headings == ["Hello World"]
    assert parser.links[0]["url"] == "https://example.com/vehicle"
    assert parser.links[0]["text"] == "Vehicle"
    assert parser.images == ["https://example.com/image.png"]
    assert parser.json_ld[0]["name"] == "Demo"


def test_scraper_blocks_local_targets():
    import pytest

    with pytest.raises(ValueError):
        _validate_url("http://127.0.0.1:8000/")


def test_version():
    assert APP_VERSION == "5.0.0"


def test_scraper_rejects_mismatched_ports():
    import pytest

    with pytest.raises(ValueError):
        _validate_url("https://example.com:80/")
    with pytest.raises(ValueError):
        _validate_url("http://example.com:443/")


def test_crawl_rejects_invalid_max_bytes():
    import pytest

    with pytest.raises(ValueError):
        crawl_site("https://example.com/", max_bytes=0)
