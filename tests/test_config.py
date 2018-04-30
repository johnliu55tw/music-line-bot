import unittest
from unittest import mock

from kkbox_line_bot import config


class GetEnvRaiseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('kkbox_line_bot.config.os')
    def test_getenv_raise(self, m_os):
        result = config.getenv_raise('SOME_ENV_VAR')

        m_os.getenv.assert_called_with('SOME_ENV_VAR', None)
        self.assertEqual(result, m_os.getenv.return_value)

    @mock.patch('kkbox_line_bot.config.os')
    def test_getenv_raise_not_exist(self, m_os):
        m_os.getenv.return_value = None

        with self.assertRaisesRegex(ValueError, r'Environment variable.*not exist'):
            config.getenv_raise('SOME_NOTEXIST_ENV_VAR')


class LoadProductionTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load_default(self):
        result = config.load_default()
        self.assertIsInstance(result, dict)
        self.assertIn('LINE_CHANNEL_ACCESS_TOKEN', result)
        self.assertIn('LINE_CHANNEL_SECRET', result)
        self.assertIn('OLAMI_APP_KEY', result)
        self.assertIn('OLAMI_APP_SECRET', result)
        self.assertIn('KKBOX_ACCESS_TOKEN', result)

    @mock.patch('kkbox_line_bot.config.getenv_raise')
    def test_load_production(self, m_getenv_raise):
        m_getenv_raise.side_effect = ['first_val', 'second_val', 'third_val', 'forth_val',
                                      'fifth_val']

        result = config.load_production()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['LINE_CHANNEL_ACCESS_TOKEN'], 'first_val')
        self.assertEqual(result['LINE_CHANNEL_SECRET'], 'second_val')
        self.assertEqual(result['OLAMI_APP_KEY'], 'third_val')
        self.assertEqual(result['OLAMI_APP_SECRET'], 'forth_val')
        self.assertEqual(result['KKBOX_ACCESS_TOKEN'], 'fifth_val')

    @mock.patch('kkbox_line_bot.config.getenv_raise')
    def test_load_production_error(self, m_getenv_raise):
        m_getenv_raise.side_effect = ValueError('Mocked Error')

        with self.assertRaises(ValueError):
            config.load_production()
