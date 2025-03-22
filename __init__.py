from .core.static_scrapper import StaticScraper
from .storage.json_storage import JSONStorage

# Configuración del scraper
scraper = StaticScraper(use_proxies=True, simulate_human=True)

# Realizar scraping de una URL
url = "https://example.com"
data = scraper.scrape(url)

# Guardar datos en un archivo JSON
images  = scraper.image_extractor()
storage = JSONStorage("data/scraped_data.json")
storage.save_data(data)
