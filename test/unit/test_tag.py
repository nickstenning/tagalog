from ..helpers import assert_equal
from tagalog import tag


def test_tag_no_tags():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = tag(data, ['foobar', 'baz'])

    assert_equal(next(out), {'@message': 'one',
                              '@tags': ['foobar', 'baz']})
    assert_equal(next(out), {'@message': 'two',
                              '@tags': ['foobar', 'baz']})

def test_tag_custom_key():
    data = [{'msg': 'one'},
            {'msg': 'two'}]
    out = tag(data, ['foobar', 'baz'], key='tags')

    assert_equal(next(out), {'msg': 'one',
                              'tags': ['foobar', 'baz']})
    assert_equal(next(out), {'msg': 'two',
                              'tags': ['foobar', 'baz']})

def test_tag_null_tags():
    data = [{'@message': 'one', '@tags': None},
            {'@message': 'two', '@tags': None}]
    out = tag(data, ['foobar', 'baz'])

    assert_equal(next(out), {'@message': 'one',
                              '@tags': ['foobar', 'baz']})
    assert_equal(next(out), {'@message': 'two',
                              '@tags': ['foobar', 'baz']})


def test_tag_append_tags():
    data = [{'@message': 'one', '@tags': ['wibble']},
            {'@message': 'two', '@tags': []}]
    out = tag(data, ['foobar', 'baz'])

    assert_equal(next(out), {'@message': 'one',
                              '@tags': ['wibble', 'foobar', 'baz']})
    assert_equal(next(out), {'@message': 'two',
                              '@tags': ['foobar', 'baz']})


def test_dont_tag():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = tag(data)

    assert_equal(next(out), {'@message': 'one'})
    assert_equal(next(out), {'@message': 'two'})


def test_tag_replaces_nonextendable_value():
    data = [{'@message': 'one', '@tags': 'a string'}]
    out = tag(data, ['foobar', 'baz'])

    assert_equal(next(out), {'@message': 'one', '@tags': ['foobar', 'baz']})


def test_tag_copies():
    data = [{'@message': 'one'}]

    tags = ['foobar', 'baz']
    out = tag(data, tags)

    res = next(out)

    tags.append('bat')
    assert_equal(res, {'@message': 'one', '@tags': ['foobar', 'baz']})
