
import pytest
import os
from datetime import datetime
import taskhuddler.utils as utils
from dateutil.parser import parse
from unittest.mock import patch
import boto3
import botocore
from moto import mock_s3

Range = utils.Range


@pytest.mark.parametrize("r1,r2,expected", (
    (Range(start=datetime(2017, 1, 15), end=datetime(2017, 5, 10)),
     Range(start=datetime(2017, 3, 20), end=datetime(2017, 9, 15)), True),
    (Range(start=datetime(2017, 6, 15), end=datetime(2017, 6, 15)),
     Range(start=datetime(2017, 6, 11), end=datetime(2017, 6, 18)), True),
    (Range(start=datetime(2017, 1, 10), end=datetime(2017, 5, 10)),
     Range(start=datetime(2017, 6, 10), end=datetime(2017, 9, 10)), False),
    (Range(start=parse("2017-06-10 09:00:00"), end=parse("2017-06-10 10:00:00")),
     Range(start=parse("2017-06-10 09:50:00"), end=parse("2017-06-10 10:10:00")),
     True),
    (Range(start=parse("2017-06-10 09:00:00"), end=parse("2017-06-10 10:00:00")),
     Range(start=parse("2017-06-10 10:50:00"), end=parse("2017-06-11 10:10:00")),
     False),
))
def test_should_merge(r1, r2, expected):
    assert utils.should_merge(r1, r2) == expected


@pytest.mark.parametrize("r1,r2,expected", (
    (Range(start=datetime(2017, 1, 15), end=datetime(2017, 5, 10)),
     Range(start=datetime(2017, 3, 20), end=datetime(2017, 9, 15)),
     Range(start=datetime(2017, 1, 15), end=datetime(2017, 9, 15))),
    (Range(start=datetime(2017, 6, 15), end=datetime(2017, 6, 15)),
     Range(start=datetime(2017, 6, 11), end=datetime(2017, 6, 18)),
     Range(start=datetime(2017, 6, 11), end=datetime(2017, 6, 18))),
    (Range(start=datetime(2017, 5, 5), end=datetime(2017, 5, 10)),
     Range(start=datetime(2017, 5, 1), end=datetime(2017, 5, 15)),
     Range(start=datetime(2017, 5, 1), end=datetime(2017, 5, 15))),
))
def test_merge_dates(r1, r2, expected):
    assert utils.merge_dates(r1, r2) == expected


@pytest.mark.parametrize("r1,r2", (
    (Range(start=datetime(2017, 1, 10), end=datetime(2017, 5, 10)),
     Range(start=datetime(2017, 6, 10), end=datetime(2017, 9, 10))),
))
def test_merge_dates_bad_args(r1, r2):
    with pytest.raises(ValueError):
        utils.merge_dates(r1, r2)


@pytest.mark.parametrize("dt_list,expected", [
    ([
        Range(start=datetime(2017, 1, 15), end=datetime(2017, 2, 15)),
        Range(start=datetime(2017, 5, 1), end=datetime(2017, 5, 15)),
        Range(start=datetime(2017, 2, 1), end=datetime(2017, 2, 25)),
        Range(start=datetime(2017, 5, 5), end=datetime(2017, 5, 10)),
        Range(start=datetime(2017, 5, 14), end=datetime(2017, 6, 29)),
    ],
        [
        Range(start=datetime(2017, 1, 15), end=datetime(2017, 2, 25)),
        Range(start=datetime(2017, 5, 1), end=datetime(2017, 6, 29)),
    ])
])
def test_merge_date_list(dt_list, expected):
    assert utils.merge_date_list(dt_list) == expected


def test_fetch_file_local():
    contents = utils.fetch_file(os.path.join(os.path.dirname(__file__), 'data', 'dummyfile.txt'))
    assert contents == "test data"


def test_store_file_local():
    filename = os.path.join(os.path.dirname(__file__), 'data', 'dummyfile2.txt')
    utils.store_file(filename, 'test data')
    contents = utils.fetch_file(filename)
    assert contents == "test data"


@mock_s3
def test_fetch_file_s3():
    expected = b"test data"
    client = boto3.client('s3', aws_access_key_id='foobar', aws_secret_access_key='foobar')
    client.create_bucket(Bucket='dummy')
    client.put_object(Body=expected, Bucket='dummy', Key='dummyfile.txt')

    assert utils.fetch_file('s3://dummy/dummyfile.txt') == expected


@mock_s3
def test_fetch_file_s3_raises():
    client = boto3.client('s3', aws_access_key_id='foobar', aws_secret_access_key='foobar')
    client.create_bucket(Bucket='dummy')
    with pytest.raises(botocore.exceptions.ClientError):
        utils.fetch_file('s3://dummy/dummyfile.txt')


@mock_s3
def test_store_file_s3():
    expected = b"test data"
    client = boto3.client('s3', aws_access_key_id='foobar', aws_secret_access_key='foobar')
    client.create_bucket(Bucket='dummy')
    utils.store_file('s3://dummy/dummyfile.txt', expected)
    assert utils.fetch_file('s3://dummy/dummyfile.txt') == expected
