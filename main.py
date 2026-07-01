from core.logger import Logger
from core.config_manager import ConfigManager



log = Logger()

log.info("Translate VN iniciado.")
log.info("Criando projeto...")
log.warning("Arquivo não encontrado.")
log.error("Falha ao abrir o projeto.")


config = ConfigManager()

print(config.get("language"))

config.set("language", "en_US")

config.set("theme", "light")