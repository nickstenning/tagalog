from ..helpers import assert_equal, patch
import datetime
from tagalog import stamp

@patch('tagalog._now')
def test_stamp(now_mock):
    now_mock.side_effect = [datetime.datetime(2013, 1, 1, 9, 0, 1, 0),
                            datetime.datetime(2013, 1, 1, 9, 0, 2, 100),
                            datetime.datetime(2013, 1, 1, 9, 0, 3, 200)]

    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = stamp(data)
    assert_equal(next(out),
                 {'@timestamp': '2013-01-01T09:00:01.000000Z',
                  '@message': 'one'})
    assert_equal(next(out),
                 {'@timestamp': '2013-01-01T09:00:02.000100Z',
                  '@message': 'two'})
    assert_equal(next(out),
                 {'@timestamp': '2013-01-01T09:00:03.000200Z',
                  '@message': 'three'})

@patch('tagalog._now')
def test_stamp_key(now_mock):
    now_mock.side_effect = [datetime.datetime(2013, 1, 1, 9, 0, 1, 0),
                            datetime.datetime(2013, 1, 1, 9, 0, 2, 100),
                            datetime.datetime(2013, 1, 1, 9, 0, 3, 200)]

    data = [{'msg': 'one'},
            {'msg': 'two'},
            {'msg': 'three'}]
    out = stamp(data, key='ts')
    assert_equal(next(out),
                 {'ts': '2013-01-01T09:00:01.000000Z',
                  'msg': 'one'})
    assert_equal(next(out),
                 {'ts': '2013-01-01T09:00:02.000100Z',
                  'msg': 'two'})
    assert_equal(next(out),
                 {'ts': '2013-01-01T09:00:03.000200Z',
                  'msg': 'three'})

