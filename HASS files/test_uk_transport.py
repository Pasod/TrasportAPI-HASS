"""The tests for the uk_transport platform."""
import re
from datetime import timedelta

import requests_mock
import unittest

from homeassistant.components.sensor.uk_transport import (
    UkTransportSensor,
    ATTR_ATCOCODE, ATTR_LOCALITY, ATTR_STOP_NAME, ATTR_NEXT_BUSES,
    CONF_API_APP_KEY, CONF_API_APP_ID, CONF_LIVE_BUS_TIME,
    CONF_STOP_ATCOCODE, CONF_BUS_DIRECTION, SCAN_INTERVAL)
from homeassistant.setup import setup_component
from tests.common import load_fixture, get_test_home_assistant

BUS_ATCOCODE = '340000368SHE'
BUS_DIRECTION = 'Wantage'

VALID_CONFIG = {
    'platform': 'uk_transport',
    CONF_API_APP_ID: 'foo',
    CONF_API_APP_KEY: 'ebcd1234',
    SCAN_INTERVAL: timedelta(seconds=180),
    CONF_LIVE_BUS_TIME: [{
        CONF_STOP_ATCOCODE: BUS_ATCOCODE,
        CONF_BUS_DIRECTION: BUS_DIRECTION}],
}


class TestUkTransportSensor(unittest.TestCase):
    """Test the uk_transport platform."""

    def setUp(self):
        """Initialize values for this testcase class."""
        self.hass = get_test_home_assistant()
        self.config = VALID_CONFIG

    def tearDown(self):
        """Stop everything that was started."""
        self.hass.stop()

    @requests_mock.Mocker()
    def test_setup(self, mock_req):
        """Test for operational uk_transport sensor with proper attributes."""
        with requests_mock.Mocker() as mock_req:
            uri = re.compile(UkTransportSensor.TRANSPORT_API_URL_BASE + '*')
            mock_req.get(uri, text=load_fixture('uk_transport_bus.json'))
            self.assertTrue(
                setup_component(self.hass, 'sensor', {'sensor': self.config}))

        bus_state = self.hass.states.get('sensor.next_bus_to_wantage')

        assert type(bus_state.state) == str
        assert bus_state.name == 'Next bus to {}'.format(BUS_DIRECTION)
        assert bus_state.attributes.get(ATTR_ATCOCODE) == BUS_ATCOCODE
        assert bus_state.attributes.get(ATTR_LOCALITY) == 'Harwell Campus'
        assert bus_state.attributes.get(ATTR_STOP_NAME) == 'Bus Station'
        assert len(bus_state.attributes.get(ATTR_NEXT_BUSES)) == 2

        direction_re = re.compile(BUS_DIRECTION)
        for bus in bus_state.attributes.get(ATTR_NEXT_BUSES):
            print(bus['direction'], direction_re.match(bus['direction']))
            assert direction_re.search(bus['direction']) is not None
