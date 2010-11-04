from naya.conf import Config
from naya.testing import aye


CONFIG = {'a': 1, 'b': {'a': 2, 'b': {'a': 3}}, 'a0': 0, '_a': 0, 'a_0': 0}
CONFIG_FAIL = (
    {1: 1},
    {'a:b': 1},
    {'a': 1, 'b:c': {'a': 2}},
    {'0': 1},
    {'0a': 1},
    {'_0a-': 1},
    {'a-': 1},
    {'-': 1},
)


def test_config_get():
    conf = Config(CONFIG)

    aye('==', 1, conf['a'])
    aye('==', 2, conf['b:a'])
    aye('==', 3, conf['b:b:a'])

    aye('==', 1, conf.get('a'))
    aye('==', 2, conf.get('b:a'))
    aye('==', 3, conf.get('b:b:a'))
    aye('==', None, conf.get('b:d'))


def test_config_update():
    conf = Config(CONFIG)

    conf.update({'c': 10})
    aye('==', 3, conf['b:b:a'])
    aye('==', 10, conf['c'])

    conf.update({'b': {'c': 20}})
    aye('==', 2, conf['b:a'])
    aye('==', 20, conf['b:c'])

    conf.update({'b': {'b': {'c': 30}}})
    aye('==', 3, conf['b:b:a'])
    aye('==', 30, conf['b:b:c'])

    conf['b:d'] = []
    conf.update({'b': {'d': {'a': 1}}})
    aye('==', 1, conf['b:d:a'])


def test_config_set():
    conf = Config(CONFIG)

    conf['b:b:c'] = 30
    aye('==', 3, conf['b:b:a'])
    aye('==', 30, conf['b:b:c'])

    conf['b:b'] = 30
    aye('==', 30, conf['b:b'])

    conf['b:'] = 0
    aye('==', 2, conf['b:a'])
    aye('==', 0, conf['b:'])

    conf['b:b'] = {'f': 42}
    aye('==', 42, conf['b:b:f'])

    conf['b:b'] = {'b': {'d': {'a': 1}}}
    aye('==', 42, conf['b:b:f'])
    aye('==', 1, conf['b:b:b:d:a'])


def test_config_fail():
    conf = Config(CONFIG)

    aye.raises(KeyError, lambda: conf['b:a:c'])
    aye.raises(KeyError, lambda: conf['d'])
    aye.raises(KeyError, lambda: conf['b:d'])

    for prefs in CONFIG_FAIL:
        aye.raises(KeyError, lambda: Config(prefs))

    for prefs in CONFIG_FAIL:
        aye.raises(KeyError, lambda: conf.update(prefs))

    for prefs in CONFIG_FAIL:
        aye.raises(KeyError, lambda: conf.__setitem__('b:b', prefs))


def test_config_contains():
    conf = Config(CONFIG)

    aye('in', 'a', conf)
    aye('in', 'b:a', conf)
    aye('not in', 'b:c', conf)
