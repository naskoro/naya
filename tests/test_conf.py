from nose.tools import *

from naya.conf import Config


CONFIG = {'a': 1, 'b': {'a': 2, 'b': {'a': 3}}}
CONFIG_FAIL = {'a:b': 1}
CONFIG_FAIL2 = {'a': 1, 'b:c': {'a': 2}}


def test_config_get():
    conf = Config(CONFIG)

    eq_(1, conf['a'])
    eq_(2, conf['b:a'])
    eq_(3, conf['b:b:a'])

    eq_(1, conf.get('a'))
    eq_(2, conf.get('b:a'))
    eq_(3, conf.get('b:b:a'))
    eq_(None, conf.get('b:d'))


def test_config_update():
    conf = Config(CONFIG)

    conf.update({'c': 10})
    eq_(3, conf['b:b:a'])
    eq_(10, conf['c'])

    conf.update({'b': {'c': 20}})
    eq_(2, conf['b:a'])
    eq_(20, conf['b:c'])

    conf.update({'b': {'b': {'c': 30}}})
    eq_(3, conf['b:b:a'])
    eq_(30, conf['b:b:c'])


def test_config_set():
    conf = Config(CONFIG)

    conf['b:b:c'] = 30
    eq_(3, conf['b:b:a'])
    eq_(30, conf['b:b:c'])

    conf['b:b'] = 30
    eq_(30, conf['b:b'])

    conf['b:'] = 0
    eq_(2, conf['b:a'])
    eq_(0, conf['b:'])


def test_config_fail():
    conf = Config(CONFIG)

    assert_raises(KeyError, lambda: conf['b:a:c'])
    assert_raises(KeyError, lambda: conf['d'])
    assert_raises(KeyError, lambda: conf['b:d'])

    assert_raises(KeyError, lambda: Config(CONFIG_FAIL))
    assert_raises(KeyError, lambda: Config(CONFIG_FAIL2))

    assert_raises(KeyError, lambda: conf.update(CONFIG_FAIL))
    assert_raises(KeyError, lambda: conf.update(CONFIG_FAIL2))
