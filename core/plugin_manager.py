"""
plugin_manager.py

Gerenciador central de plugins do Translate VN.

Copie este arquivo para: Translate_VN/core/plugin_manager.py
"""

import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type
from dataclasses import dataclass
import urllib.request
import zipfile
import io
import shutil

from plugin_base import PluginBase, PluginMetadata


@dataclass
class PluginInfo:
    """Informação sobre um plugin instalado"""
    name: str
    path: Path
    metadata: PluginMetadata
    instance: Optional[PluginBase] = None
    enabled: bool = False


class PluginManager:
    """
    Gerenciador central de plugins.
    
    Uso:
        manager = PluginManager(plugins_dir="plugins", logger=logger)
        manager.discover_plugins()
        manager.install_from_github("https://github.com/user/plugin-name")
        manager.enable_plugin("plugin-name")
    """
    
    def __init__(self, 
                 plugins_dir: str = "plugins",
                 config_file: str = "plugins/plugins_config.json",
                 logger = None):
        
        self.plugins_dir = Path(plugins_dir)
        self.config_file = Path(config_file)
        self.logger = logger
        
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_modules: Dict[str, any] = {}
        self.registry: Dict[str, any] = {}
        
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._load_registry()
    
    def _log(self, level: str, message: str):
        """Log wrapper"""
        if self.logger:
            getattr(self.logger, level.lower(), print)(message)
        else:
            print(f"[{level}] {message}")
    
    def _load_registry(self):
        """Carrega registro persistido de plugins"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
        except Exception as e:
            self._log("WARNING", f"Erro ao carregar registry de plugins: {e}")
            self.registry = {}
    
    def _save_registry(self):
        """Salva registro de plugins no disco"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log("ERROR", f"Erro ao salvar registry: {e}")
    
    # ===================================================
    # Descoberta automática de plugins
    # ===================================================
    
    def discover_plugins(self) -> List[str]:
        """
        Descobre plugins instalados procurando por pastas com plugin.json.
        
        Returns:
            Lista de nomes de plugins descobertos
        """
        discovered = []
        
        if not self.plugins_dir.exists():
            self._log("WARNING", f"Diretório de plugins não existe: {self.plugins_dir}")
            return discovered
        
        for plugin_dir in self.plugins_dir.iterdir():
            
            if not plugin_dir.is_dir() or plugin_dir.name.startswith('_'):
                continue
            
            plugin_json = plugin_dir / "plugin.json"
            
            if not plugin_json.exists():
                continue
            
            try:
                with open(plugin_json, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)
                
                metadata = PluginMetadata.from_dict(metadata_dict)
                
                info = PluginInfo(
                    name=metadata.name,
                    path=plugin_dir,
                    metadata=metadata,
                    enabled=metadata.enabled,
                )
                
                self.plugins[metadata.name] = info
                discovered.append(metadata.name)
                
                self._log("INFO", f"Plugin descoberto: {metadata.name} v{metadata.version}")
            
            except Exception as e:
                self._log("ERROR", f"Erro ao descobrir plugin em {plugin_dir}: {e}")
        
        return discovered
    
    # ===================================================
    # Carregamento dinâmico de plugins
    # ===================================================
    
    def load_plugin_module(self, plugin_name: str) -> Optional[any]:
        """Carrega o módulo Python de um plugin."""
        if plugin_name not in self.plugins:
            self._log("ERROR", f"Plugin não descoberto: {plugin_name}")
            return None
        
        plugin_info = self.plugins[plugin_name]
        plugin_path = plugin_info.path
        
        if str(plugin_path) not in sys.path:
            sys.path.insert(0, str(plugin_path))
        
        # Tentar __init__.py
        init_file = plugin_path / "__init__.py"
        if init_file.exists():
            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_name}",
                    init_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                self.loaded_modules[plugin_name] = module
                self._log("INFO", f"Módulo carregado: {plugin_name}")
                return module
            
            except Exception as e:
                self._log("ERROR", f"Erro ao carregar módulo {init_file}: {e}")
        
        # Fallback: main.py
        main_file = plugin_path / "main.py"
        if main_file.exists():
            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_name}_main",
                    main_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                self.loaded_modules[plugin_name] = module
                return module
            
            except Exception as e:
                self._log("ERROR", f"Erro ao carregar módulo {main_file}: {e}")
        
        self._log("ERROR", f"Nenhum módulo Python encontrado para {plugin_name}")
        return None
    
    def get_plugin_class(self, plugin_name: str) -> Optional[Type[PluginBase]]:
        """Encontra a classe PluginBase no módulo do plugin."""
        module = self.load_plugin_module(plugin_name)
        
        if not module:
            return None
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if isinstance(attr, type) and issubclass(attr, PluginBase) and attr != PluginBase:
                return attr
        
        self._log("ERROR", f"Nenhuma classe PluginBase encontrada em {plugin_name}")
        return None
    
    # ===================================================
    # Ativação e desativação
    # ===================================================
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Ativa um plugin descoberto."""
        if plugin_name not in self.plugins:
            self._log("ERROR", f"Plugin não descoberto: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.enabled:
            return True
        
        if not self._check_dependencies(plugin_info.metadata):
            return False
        
        plugin_class = self.get_plugin_class(plugin_name)
        if not plugin_class:
            return False
        
        try:
            instance = plugin_class()
            instance.logger = self.logger
            instance._plugin_dir = plugin_info.path
            
            config_file = plugin_info.path / "config.json"
            instance.load_config(config_file)
            
            if not instance.on_load():
                self._log("ERROR", f"on_load() retornou False para {plugin_name}")
                return False
            
            plugin_info.instance = instance
            plugin_info.enabled = True
            plugin_info.metadata.enabled = True
            
            self.registry[plugin_name] = {"enabled": True}
            self._save_registry()
            
            self._log("INFO", f"Plugin ativado: {plugin_name}")
            return True
        
        except Exception as e:
            self._log("ERROR", f"Erro ao ativar plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Desativa um plugin ativado."""
        if plugin_name not in self.plugins:
            self._log("ERROR", f"Plugin não descoberto: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if not plugin_info.enabled or not plugin_info.instance:
            return True
        
        try:
            if not plugin_info.instance.on_unload():
                self._log("WARNING", f"on_unload() retornou False para {plugin_name}")
            
            plugin_info.instance = None
            plugin_info.enabled = False
            plugin_info.metadata.enabled = False
            
            self.registry[plugin_name] = {"enabled": False}
            self._save_registry()
            
            self._log("INFO", f"Plugin desativado: {plugin_name}")
            return True
        
        except Exception as e:
            self._log("ERROR", f"Erro ao desativar plugin {plugin_name}: {e}")
            return False
    
    def _check_dependencies(self, metadata: PluginMetadata) -> bool:
        """Verifica se as dependências de um plugin estão satisfeitas"""
        for dep in metadata.dependencies:
            if dep not in self.plugins:
                self._log("WARNING", f"Dependência faltando: {dep}")
                return False
        return True
    
    # ===================================================
    # Instalação de plugins
    # ===================================================
    
    def install_from_github(self, repo_url: str, branch: str = "main") -> bool:
        """Instala um plugin a partir de um repositório GitHub."""
        repo_url = repo_url.rstrip('/')
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        self._log("INFO", f"Instalando plugin de {repo_url}...")
        
        try:
            zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
            
            self._log("INFO", "Baixando arquivo...")
            request = urllib.request.Request(
                zip_url,
                headers={"User-Agent": "TranslateVN-PluginManager"}
            )
            
            with urllib.request.urlopen(request, timeout=30) as response:
                zip_data = response.read()
            
            self._log("INFO", "Extraindo arquivo...")
            temp_dir = self.plugins_dir / "_install_temp"
            
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(io.BytesIO(zip_data)) as archive:
                archive.extractall(temp_dir)
            
            # Encontrar plugin.json
            plugin_json = None
            for candidate in temp_dir.rglob("plugin.json"):
                plugin_json = candidate
                break
            
            if not plugin_json:
                self._log("ERROR", "plugin.json não encontrado no repositório")
                return False
            
            with open(plugin_json, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            
            plugin_name = metadata_dict.get("name", repo_name)
            plugin_install_dir = self.plugins_dir / plugin_name
            
            if plugin_install_dir.exists():
                self._log("INFO", "Plugin já existe. Atualizando...")
                shutil.rmtree(plugin_install_dir)
            
            plugin_source_dir = plugin_json.parent
            shutil.copytree(plugin_source_dir, plugin_install_dir)
            
            shutil.rmtree(temp_dir)
            
            self._log("INFO", f"Plugin instalado: {plugin_name}")
            return True
        
        except Exception as e:
            self._log("ERROR", f"Erro ao instalar plugin: {e}")
            return False
    
    def install_from_local(self, local_path: str) -> bool:
        """Instala um plugin a partir de uma pasta local."""
        source_dir = Path(local_path).resolve()
        
        if not source_dir.exists():
            self._log("ERROR", f"Diretório não existe: {source_dir}")
            return False
        
        plugin_json = source_dir / "plugin.json"
        
        if not plugin_json.exists():
            self._log("ERROR", f"plugin.json não encontrado em {source_dir}")
            return False
        
        try:
            with open(plugin_json, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            
            plugin_name = metadata_dict.get("name")
            
            if not plugin_name:
                self._log("ERROR", "Nome do plugin não especificado em plugin.json")
                return False
            
            plugin_install_dir = self.plugins_dir / plugin_name
            
            if plugin_install_dir.exists():
                self._log("INFO", "Plugin já existe. Atualizando...")
                shutil.rmtree(plugin_install_dir)
            
            shutil.copytree(source_dir, plugin_install_dir)
            
            self._log("INFO", f"Plugin instalado: {plugin_name}")
            return True
        
        except Exception as e:
            self._log("ERROR", f"Erro ao instalar plugin: {e}")
            return False
    
    # ===================================================
    # Consultas
    # ===================================================
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Retorna instância de um plugin ativado"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].instance
        return None
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Retorna informações sobre um plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self, enabled_only: bool = False) -> List[PluginInfo]:
        """Lista plugins descobertos"""
        plugins = list(self.plugins.values())
        
        if enabled_only:
            plugins = [p for p in plugins if p.enabled]
        
        return sorted(plugins, key=lambda p: p.name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[PluginBase]:
        """Retorna todos os plugins ativados de um tipo específico"""
        results = []
        
        for info in self.plugins.values():
            if info.enabled and info.metadata.plugin_type == plugin_type:
                if info.instance:
                    results.append(info.instance)
        
        return results
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Desinstala um plugin completamente."""
        if plugin_name not in self.plugins:
            self._log("ERROR", f"Plugin não encontrado: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.enabled:
            self.disable_plugin(plugin_name)
        
        try:
            shutil.rmtree(plugin_info.path)
            
            if plugin_name in self.registry:
                del self.registry[plugin_name]
            
            del self.plugins[plugin_name]
            
            self._save_registry()
            
            self._log("INFO", f"Plugin desinstalado: {plugin_name}")
            return True
        
        except Exception as e:
            self._log("ERROR", f"Erro ao desinstalar plugin: {e}")
            return False