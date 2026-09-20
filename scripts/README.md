# Scraper CLI

Jalankan dari root repository:

    python scripts/scraper.py https://example.com

Crawl domain yang sama:

    python scripts/scraper.py https://example.com --crawl --max-pages 5

Simpan hasil JSON:

    python scripts/scraper.py https://example.com --output reports/example.json

Scraper memeriksa host publik, membatasi ukuran response, timeout, dan mematuhi robots.txt bila tersedia.
