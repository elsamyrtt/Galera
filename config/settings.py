import os

# Configuración general del proyecto
PROJECT_NAME = "Galera"

# Configuración de scraping
SCRAPING_CONFIG = {
    "use_proxies": True,
    "simulate_human": True,
    "solve_captchas": True,
    "concurrency": 10,
    "retry_attempts": 3,
    "request_delay": (1, 5),
    "user_agent_rotation": True,
    "headers": {
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    },
    "timeout": 30,
}

# Configuración de almacenamiento
STORAGE_CONFIG = {
    "csv": {
        "file_path": os.path.join(os.getcwd(), "data", "scraped_data.csv")
    },
    "json": {
        "file_path": os.path.join(os.getcwd(), "data", "scraped_data.json")
    },
    "sqlite": {
        "db_path": os.path.join(os.getcwd(), "data", "scraped_data.db")
    },
    "mongo": {
        "uri": "mongodb://localhost:27017/",
        "db_name": "galera",
        "collection_name": "scraped_data"
    },
    "postgres": {
        "host": "localhost",
        "dbname": "galera",
        "user": "your_user",
        "password": "your_password"
    },
    "elasticsearch": {
        "hosts": ["http://localhost:9200"],
        "index_name": "scraped_data"
    }
}

# Configuración de plataformas
PLATFORMS_CONFIG = {
    "wikipedia": {
        "base_url": "https://en.wikipedia.org"
    },
    "reddit": {
        "base_url": "https://www.reddit.com"
    },
    "twitter": {
        "base_url": "https://twitter.com"
    },
    "linkedin": {
        "base_url": "https://www.linkedin.com"
    },
    "fandom": {
        "base_url": "https://www.fandom.com"
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(os.getcwd(), "logs", "galera.log"),
            "formatter": "standard",
        },
    },
    "loggers": {
        "galera": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
