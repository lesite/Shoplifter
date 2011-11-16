from unittest import TestCase
from shoplifter.core.config import PluginHost


class TestPlugin(TestCase):
    def test_plugin_load(self):
        pls = PluginHost('shoplifter')
        self.assertTrue('temp_storage' in pls.available_plugins.keys())
        self.assertFalse('temp_storage' in pls.loaded_plugins.keys())

        # Test loading plugins.
        pls.load('temp_storage', 'dummy', None, 'asd')
        self.assertTrue('temp_storage' in pls.loaded_plugins.keys())

        # Check that you can access loaded plugins using dictionary
        # like syntax.
        self.assertEquals(
            pls['temp_storage'], pls.loaded_plugins['temp_storage'])
