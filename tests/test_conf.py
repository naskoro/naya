from naya.conf import Config
from naya.testing import aye, raises


CONFIG = {'a': 1, 'b': {'a': 2, 'b': {'a': 3}}, 'a0': 0, '_a': 0, 'a_0': 0}
CONFIG_FAIL = (
    ({1: 1}, 1),
    ({'a:b': 1}, 'a:b'),
    ({'a': 1, 'b:c': {'a': 2}}, 'b:c'),
    ({'0': 1}, '0'),
    ({'0a': 1}, '0a'),
    ({'_0a-': 1}, '_0a-'),
    ({'-': 1}, '-'),
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

    conf['b:d'].update(None)
    aye('==', 1, conf['b:d:a'])


def test_config_set():
    conf = Config(CONFIG)

    conf['c:b'] = 42
    aye('==', 42, conf['c:b'])

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
    def check_set(conf, key, value):
        def inner():
            conf[key] = value
        return inner

    conf = Config(CONFIG)

    e = raises(KeyError, lambda: conf['b:a:c'])
    aye('==', e.args, ('a:c',))

    e = raises(KeyError, lambda: conf['d'])
    aye('==', e.args, ('d',))

    e = raises(KeyError, lambda: conf['b:d'])
    aye('==', e.args, ('d',))

    e = raises(KeyError, check_set(conf, 'a:42', 42))
    aye('==', e.args, ('conf[\'a\'] = 1, not dict',))

    for prefs, key in CONFIG_FAIL:
        e = raises(KeyError, lambda: Config(prefs))
        aye('in', '%r not match' % key, e.args[0])

    for prefs, key in CONFIG_FAIL:
        e = raises(KeyError, lambda: conf.update(prefs))
        aye('in', '%r not match' % key, e.args[0])

    for prefs, key in CONFIG_FAIL:
        e = raises(KeyError, check_set(conf, 'b:b', prefs))
        aye('in', '%r not match' % key, e.args[0])


def test_config_contains():
    conf = Config(CONFIG)

    aye('in', 'a', conf)
    aye('in', 'b:a', conf)
    aye('not in', 'b:c', conf)
