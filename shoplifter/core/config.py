import pkg_resources
from marrow.util.bunch import Bunch


class PluginHost(object):
    """
    Plugin host is used to automatically find entry points that match
    the entry point groups the __package__ advertises, and provides
    ways to load those plugins easily.
    """

    def __init__(self, distribution, package=None):
        self.available_plugins = Bunch()
        self.loaded_plugins = Bunch()

        # Find entry points.
        try:
            self._find_plugins(distribution, package)
        except pkg_resources.DistributionNotFound:
            # This will be raised when the package is installing for example.
            pass

    def __getitem__(self, key):
        # In order to access loaded plugins as dictionary.
        return self.loaded_plugins[key]

    def _find_plugins(self, distribution, package=None):
        """
        This populates self.available_plugins
        """
        distribution = pkg_resources.get_distribution(distribution)

        for group in distribution.get_entry_map().keys():

            if package and group.startswith(package):
                group_name = group.split(package)[1].strip('.')
            elif not package:
                group_name = group
            else:
                continue

            self.available_plugins[group_name] = Bunch()

            # Load entry points in plugin dict.
            for x in pkg_resources.iter_entry_points(group):
                self.available_plugins[group_name][x.name] = x

    def load(self, group, plugin_name, *args, **kwargs):
        """
        Load a plugin (calling entry_point.load() and passing *args
        and **kwargs to loaded plugin.
        """

        # Create a Bunch as self[entry_point.group] if it doesn't yet exist.
        if group not in self.loaded_plugins:
            self.loaded_plugins[group] = Bunch()

        # Instantiate plugin with supplied args and kwargs.
        self.loaded_plugins[group][plugin_name] = (
            self.available_plugins[group][plugin_name].load()(
                *args, **kwargs))


class Config(Bunch):
    """
    A simple configuration class that can be used to store arbitrary data.
    """
    pass
