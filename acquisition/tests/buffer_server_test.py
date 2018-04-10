import pytest
import time
import unittest

import buffer_server
import logging
from record import Record
import numpy as np


class ClassName(object):
    """docstring for ClassName"""

    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg


class TestBufferServer(unittest.TestCase):
    """Tests for the buffer_server module."""

    def __init__(self, *args, **kwargs):
        super(TestBufferServer, self).__init__(*args, **kwargs)
        self.i = 1

    def _next_buf_name(self):
        name = 'buffer_{}.db'.format(self.i)
        self.i += 1
        return name

    def setUp(self):
        """Run before each test."""
        self.channel_count = 25
        self.channels = ["ch" + str(c) for c in range(self.channel_count)]
        self.pid = buffer_server.start(self.channels, self._next_buf_name())

    def tearDown(self):
        """Run after each test."""
        buffer_server.stop(self.pid)
        self.pid = None

    def _new_data(self):
        """Generates a data row with a float for each channel."""

        return [np.random.uniform(-1000, 1000) for cc in
                range(self.channel_count)]

    def test_count(self):
        n = 500
        for i in range(n):
            d = self._new_data()
            buffer_server.append(self.pid, Record(data=d, timestamp=i))

        self.assertEqual(buffer_server.count(self.pid), n)

    def test_get_data_slice(self):
        n = 150
        data = [self._new_data() for x in range(n)]
        for i, d in enumerate(data):
            buffer_server.append(self.pid, Record(data=d, timestamp=i))

        start = 10
        end = 20

        result = buffer_server.get_data(self.pid, start, end)
        self.assertEqual([r.data for r in result], data[start:end], "Should \
            return the slice of data requested.")

    def test_get_all_data(self):
        n = 150
        data = [self._new_data() for x in range(n)]
        for i, d in enumerate(data):
            buffer_server.append(self.pid, Record(data=d, timestamp=i))

        result = buffer_server.get_data(self.pid)
        self.assertEqual([r.data for r in result], data, "Should return all \
            data")

    def test_multiple_servers(self):
        pid2 = buffer_server.start(self.channels, self._next_buf_name())

        n = 200
        for i in range(n):
            d = [np.random.uniform(-1000, 1000) for cc in
                 range(self.channel_count)]
            if i % 2 == 0:
                buffer_server.append(self.pid, Record(d, i))
            else:
                buffer_server.append(pid2, Record(d, i))

        self.assertEqual(buffer_server.count(self.pid), n / 2)
        self.assertEqual(buffer_server.count(pid2), n / 2)

        server1_data = buffer_server.get_data(self.pid, 0, 5)
        server2_data = buffer_server.get_data(pid2, 0, 5)

        self.assertNotEqual(server1_data, server2_data)
        buffer_server.stop(pid2)
