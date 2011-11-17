from shoplifter.core.config import PluginHost

from unittest import TestCase
from nose.tools import assert_equals, assert_is_instance


class PluginSpecs(TestCase):
    def can_load_plugins_for_package(self):
        # Load plugins for a package part of a distribution.
        pls = PluginHost('shoplifter', 'shoplifter.core')
        assert('temp_storage' in pls.available_plugins.keys())
        assert(not 'temp_storage' in pls.loaded_plugins.keys())

        # Test loading plugins.
        pls.load('temp_storage', 'dummy', None, 'asd')
        assert('temp_storage' in pls.loaded_plugins.keys())

        # Check that you can access loaded plugins using dictionary
        # like syntax.
        assert_equals(
            pls['temp_storage'], pls.loaded_plugins['temp_storage'])

        for key in pls.available_plugins.keys():
            group = pls.available_plugins[key]
            for ep_key in group.keys():
                entry_point = group[ep_key]
                assert(entry_point.module_name.startswith('shoplifter.core'))

    def can_load_plugins_for_distribution(self):
        # Load plugins for distribution.
        pls = PluginHost('shoplifter')
        assert('shoplifter.core.temp_storage' in pls.available_plugins.keys())
        assert(not 'shoplifter.core.temp_storage' in pls.loaded_plugins.keys())

        # Test loading plugins.
        pls.load('shoplifter.core.temp_storage', 'dummy', None, 'asd')
        assert('shoplifter.core.temp_storage' in pls.loaded_plugins.keys())

        # Check that you can access loaded plugins using dictionary
        # like syntax.
        assert_equals(
            pls['shoplifter.core.temp_storage'],
            pls.loaded_plugins['shoplifter.core.temp_storage'])

    def it_doesnt_fail_when_distribution_does_not_exist(self):
        # During installation, the distribution is not yet installed
        # therefore instantiation of PluginHost should not raise
        # pkg_resources.DistributionNotFound
        pls = PluginHost('herp_a_derp')
        assert_is_instance(pls, PluginHost)
        assert(len(pls.available_plugins) == 0)
        assert(len(pls.loaded_plugins) == 0)
