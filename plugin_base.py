"""
plugin_base.py

Define a classe base e interfaces para todos os plugins do Translate VN.
Todos os plugins DEVEM herdar de PluginBase e implementar os métodos obrigatórios.

Copie este arquivo para a raiz do projeto Translate_VN/
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import json


class PluginMetadata:
    """Metadados de um plugin"""
    
    def __init__(self, 
                 name: str,
                 version: str,
                 author: str,
                 description: str,
                 plugin_type: str,
                 min_version: str = "0.1.0",
                 dependencies: Optional[List[str]] = None,
                 config_schema: Optional[Dict[str, Any]] = None):
        
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.plugin_type = plugin_type  # "translator", "postprocessor", "engine", "analyzer", etc
        self.min_version = min_version
        self.dependencies = dependencies or []
        self.config_schema = config_schema or {}
        self.enabled = False
        self.installed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte metadados para dict (para salvar em JSON)"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "plugin_type": self.plugin_type,
            "min_version": self.min_version,
            "dependencies": self.dependencies,
            "config_schema": self.config_schema,
            "enabled": self.enabled,
            "installed_at": self.installed_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Reconstrói metadados a partir de um dict"""
        obj = cls(
            name=data.get("name"),
            version=data.get("version"),
            author=data.get("author"),
            description=data.get("description"),
            plugin_type=data.get("plugin_type"),
            min_version=data.get("min_version", "0.1.0"),
            dependencies=data.get("dependencies", []),
            config_schema=data.get("config_schema", {}),
        )
        obj.enabled = data.get("enabled", False)
        obj.installed_at = data.get("installed_at")
        return obj


class PluginBase(ABC):
    """
    Classe base para todos os plugins do Translate VN.
    
    Um plugin DEVE:
    1. Herdar de PluginBase (ou subclasse)
    2. Implementar get_metadata() retornando PluginMetadata
    3. Implementar on_load() para inicialização
    4. Implementar on_unload() para limpeza
    """
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.logger = None  # Será injetado pelo PluginManager
        self._plugin_dir: Optional[Path] = None
    
    @property
    def plugin_dir(self) -> Optional[Path]:
        """Diretório onde o plugin foi instalado"""
        return self._plugin_dir
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Retorna metadados do plugin.
        
        OBRIGATÓRIO. Todo plugin deve implementar isso.
        """
        pass
    
    @abstractmethod
    def on_load(self) -> bool:
        """
        Chamado quando o plugin é ativado.
        
        Faça inicializações aqui: carregar config, conectar APIs, preparar recursos.
        
        Retorna:
            True se carregou com sucesso, False caso contrário.
            Se retornar False, o plugin não será ativado.
        """
        pass
    
    @abstractmethod
    def on_unload(self) -> bool:
        """
        Chamado quando o plugin é desativado.
        
        Faça limpeza aqui: fechar conexões, liberar recursos, salvar estado.
        
        Retorna:
            True se descarregou com sucesso, False caso contrário.
        """
        pass
    
    def load_config(self, config_file: Path) -> bool:
        """Carrega configurações do plugin a partir de um arquivo JSON."""
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao carregar config do plugin: {e}")
            return False
    
    def save_config(self, config_file: Path) -> bool:
        """Salva configurações do plugin em um arquivo JSON."""
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao salvar config do plugin: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Obtém valor de config com fallback para default"""
        return self.config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """Define valor de config"""
        self.config[key] = value


# ====================================================
# Tipos específicos de plugins
# ====================================================

class TranslatorPlugin(PluginBase):
    """Base para plugins que adicionam novos serviços de tradução."""
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Traduz texto de um idioma para outro."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Retorna lista de códigos de idiomas suportados"""
        pass


class PostprocessorPlugin(PluginBase):
    """Base para plugins que processam textos após tradução."""
    
    @abstractmethod
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Processa/modifica texto traduzido."""
        pass


class AnalyzerPlugin(PluginBase):
    """Base para plugins que analisam ou geram relatórios sobre traduções."""
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados de tradução e retorna resultado."""
        pass


class EnginePlugin(PluginBase):
    """Base para plugins que adicionam suporte a novas engines (além de Ren'Py)."""
    
    @abstractmethod
    def detect_game(self, game_path: Path) -> bool:
        """Detecta se um jogo usa esta engine."""
        pass
    
    @abstractmethod
    def extract_dialogues(self, game_path: Path) -> Dict[str, str]:
        """Extrai diálogos do jogo."""
        pass
    
    @abstractmethod
    def apply_translation(self, game_path: Path, translations: Dict[str, str]) -> bool:
        """Aplica traduções ao jogo."""
        pass