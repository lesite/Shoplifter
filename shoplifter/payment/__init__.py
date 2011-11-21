from shoplifter.core.config import Config, PluginHost

__all__ = ['config', 'plugins']

plugins = PluginHost('shoplifter', __package__)
config = Config()
