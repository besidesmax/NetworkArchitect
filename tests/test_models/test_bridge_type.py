from models.bridge_type import BridgeType


def test_bridge_type_properties():
    """Verify BridgeType cost and bandwidth."""

    # test if cost and bandwidth of BridgeType are correct
    expected_bandwidth = {
        BridgeType.ETHERNET: 100,
        BridgeType.WIFI_24G: 300,
        BridgeType.WIFI_5G: 600,
        BridgeType.FIBER: 2000
    }

    expected_cost = {
        BridgeType.ETHERNET: 10,
        BridgeType.WIFI_24G: 20,
        BridgeType.WIFI_5G: 35,
        BridgeType.FIBER: 120
    }
    for bridge_type, expected in expected_bandwidth.items():
        assert bridge_type.bandwidth == expected

    for bridge_type, expected in expected_cost.items():
        assert bridge_type.cost == expected
