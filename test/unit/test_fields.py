from ..helpers import assert_equal
from tagalog import fields


def test_no_fields():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = fields(data)

    assert_equal(next(out), {'@message': 'one'})
    assert_equal(next(out), {'@message': 'two'})


def test_single_field():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = fields(data, ['foobar=baz'])

    assert_equal(next(out), {'@message': 'one',
                             '@foobar': 'baz'})
    assert_equal(next(out), {'@message': 'two',
                             '@foobar': 'baz'})


def test_multiple_fields_field():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = fields(data, ['foobar=baz', 'sausage=bacon'])

    assert_equal(next(out), {'@message': 'one',
                             '@foobar': 'baz', '@sausage': 'bacon'})
    assert_equal(next(out), {'@message': 'two',
                             '@foobar': 'baz', '@sausage': 'bacon'})

def test_existing_fields_are_overwritten_even_message():
    data = [{'@message': 'hello', '@existing': 'field'}]
    out = fields(data, ['existing=wood', 'message=chainsawed'])

    assert_equal(next(out), {'@message': 'chainsawed',
                             '@existing': 'wood'})

def test_field_without_equals_has_no_value():
    data = [{'@message': 'hello'}]
    out = fields(data, ['noequals', 'field=good'])

    assert_equal(next(out), {'@message': 'hello',
                             '@field': 'good',
                             '@noequals': ''})

