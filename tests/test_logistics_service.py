from src.logistics_service import ShipmentEvent, accept_event


def test_delivered_event_needs_proof_and_no_exception() -> None:
    assert accept_event(ShipmentEvent("SHP-1", "delivered", ["pod/SHP-1.jpg"])) is True
    assert accept_event(ShipmentEvent("SHP-1", "delivered")) is False
    assert accept_event(ShipmentEvent("SHP-1", "delivered", ["pod/SHP-1.jpg"], "address mismatch")) is False
