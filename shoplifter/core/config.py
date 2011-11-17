import pkg_resources
from marrow.util.bunch import Bunch


class PluginHost(object):
    """
    This is used to provide a simple internal API for loading and
    finding plugins that are advertised as entry points.

    Note:

    In the context of this documentation, I refer to 'distributon' any
    package or collection of packages that has a setup.py and is
    installed using distribute or setup tools.

    It can work two ways:

    1- Find plugins matching a package name.

        This is useful if you want to have more than one PluginHost in
        1 distribution (for example in shoplifter, there is are
        shoplifter.core.plugins and shoplifter.payment.plugins)

        This can be achieved by prefixing the entry point group names
        with the package name where you intend to have a plugin host
        instance, *AND* by using the optional "package" argument when
        instantiating a PluginHost, with the package name that's been
        prefixed.

        Example:

        >>> plugins = PluginHost('shoplifter', 'shoplifter.core')

        The above will find all installed entry points advertised by
        any distribution if the group name matches a group that's
        advertised by 'shoplifter', *IF* the group name is also
        prefixed by the 'package' argument. Those plugins will be made
        available in plugin_instance.available_plugins.

        For example, if you want to create a new "payment_backend" to
        be used un shoplifter.payment, in your package's setup.py, you
        should have something like this:

        >>> entry_points={
        >>>     'shoplifter.payment.payment_backends': [
        >>>         'my_payment_backend = my_distribution:SomePaymentBackend',
        >>>         ],
        >>>     },
        >>> },

        Then this payment backend will be available in
        shoplifter.payment.plugins.available_plugins['payment_backends']
        (because it's been instantiated using PluginHost('shoplifter',
        'shoplifter.payment')


    2- Find all plugins for a distribution.

        >>> plugins = PluginHost('shoplifter')

        The above will find all installed entry points with a group
        name matching a the entry point group names advertised by the
        distribution.

        Example, if a distribution's setup.py looks like this:

        >>> entry_points={
        >>>     'rainbow_makers': [
        >>>         'colorful_rainbow = my_distribution.rainbow_makers:ColorRainbowMaker',
        >>>         ],
        >>>     },

        And the code looks for plugins in PluginHost('my_distribution')

        Then another project can contribute plugins that will be available in
        plugins.available_plugins by having an entry_points entry in
        setup.py with the same group name, example:

        >>> entry_points={
        >>>     'rainbow_makers': [
        >>>         'grayscale_rainbow = my_other_distribution.rainbow_makers:GrayScaleRainbowMaker',
        >>>         ],
        >>>     },
    """

    def __init__(self, distribution, package=None):

        # Entry points will live in self.available_plugins
        self.available_plugins = Bunch()

        # Instantiated plugins will live in self.loaded_plugins
        self.loaded_plugins = Bunch()

        # Find entry points.
        try:
            self._find_plugins(distribution, package)
        except pkg_resources.DistributionNotFound:
            # I am ignoring this exception because it's always raised
            # before a distribution is installed.
            pass

    def __getitem__(self, key):
        # This allows you to access instantiated plugins using
        # self['plugin_name']
        return self.loaded_plugins[key]

    def _find_plugins(self, distribution, package=None):
        """
        This populates self.available_plugins
        """
        distribution = pkg_resources.get_distribution(distribution)

        # First get the distribution group names.
        for group in distribution.get_entry_map().keys():

            if not package:
                # Otherwise the key for available_plugins and
                # loaded_plugins is the same than the group name.
                group_name = group
            elif not group.startswith(package):
                # If the group name doesn't start with the supplied
                # package name, skip the group.
                continue
            elif group.startswith(package):
                # If package name is supplied, trim the package name
                # from group name, and use that as a key in
                # self.available_plugins and self.loaded_plugins
                group_name = group.split(package)[1].strip('.')

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
