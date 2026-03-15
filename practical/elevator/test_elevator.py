import pytest
from solution import State, Elevator, PassengerElevator, ServiceElevator, ElevatorSystem


# ---------------------------------------------------------------------------
# Level 1: Basic Elevator
# ---------------------------------------------------------------------------
class TestLevel1:
    def test_initial_state_is_idle(self):
        e = Elevator(0, 0, 10)
        assert e.get_state() == State.IDLE

    def test_initial_floor(self):
        e = Elevator(5, 0, 10)
        assert e.get_current_floor() == 5

    def test_request_changes_state_up(self):
        e = Elevator(0, 0, 10)
        e.request(5)
        assert e.get_state() == State.UP

    def test_request_changes_state_down(self):
        e = Elevator(5, 0, 10)
        e.request(2)
        assert e.get_state() == State.DOWN

    def test_step_moves_one_floor_up(self):
        e = Elevator(0, 0, 10)
        e.request(3)
        assert e.step() == 1
        assert e.step() == 2
        assert e.step() == 3

    def test_step_moves_one_floor_down(self):
        e = Elevator(5, 0, 10)
        e.request(3)
        assert e.step() == 4
        assert e.step() == 3

    def test_idle_after_reaching_destination(self):
        e = Elevator(0, 0, 10)
        e.request(2)
        e.step()
        e.step()
        assert e.get_state() == State.IDLE

    def test_step_when_idle_returns_current(self):
        e = Elevator(3, 0, 10)
        assert e.step() == 3
        assert e.get_state() == State.IDLE

    def test_multiple_requests_served_in_order(self):
        e = Elevator(0, 0, 10)
        e.request(3)
        e.request(1)
        # First go to 3
        for _ in range(3):
            e.step()
        assert e.get_current_floor() == 3
        # Then go to 1
        e.step()
        assert e.get_current_floor() == 2
        e.step()
        assert e.get_current_floor() == 1
        assert e.get_state() == State.IDLE

    def test_request_out_of_range_raises(self):
        e = Elevator(0, 0, 10)
        with pytest.raises(ValueError):
            e.request(11)
        with pytest.raises(ValueError):
            e.request(-1)

    def test_request_same_floor_stays_idle(self):
        e = Elevator(5, 0, 10)
        e.request(5)
        assert e.get_state() == State.IDLE

    def test_sequential_destinations(self):
        e = Elevator(0, 0, 10)
        e.request(5)
        e.request(10)
        for _ in range(5):
            e.step()
        assert e.get_current_floor() == 5
        assert e.get_state() == State.UP
        for _ in range(5):
            e.step()
        assert e.get_current_floor() == 10
        assert e.get_state() == State.IDLE


# ---------------------------------------------------------------------------
# Level 2: Passenger Elevator (Directional Priority)
# ---------------------------------------------------------------------------
class TestLevel2:
    def test_initial_idle(self):
        pe = PassengerElevator(0, 0, 20)
        assert pe.get_state() == State.IDLE
        assert pe.get_pending_requests() == 0

    def test_add_up_request(self):
        pe = PassengerElevator(0, 0, 20)
        pe.add_request(1, 5)
        assert pe.get_pending_requests() == 1

    def test_add_down_request(self):
        pe = PassengerElevator(10, 0, 20)
        pe.add_request(8, 3)
        assert pe.get_pending_requests() == 1

    def test_process_single_up_request(self):
        pe = PassengerElevator(0, 0, 20)
        pe.add_request(2, 8)
        result = pe.process_next()
        assert result["origin"] == 2
        assert result["destination"] == 8
        assert pe.get_current_floor() == 8

    def test_process_single_down_request(self):
        pe = PassengerElevator(10, 0, 20)
        pe.add_request(9, 3)
        result = pe.process_next()
        assert result["origin"] == 9
        assert result["destination"] == 3
        assert pe.get_current_floor() == 3

    def test_directional_priority_up_before_down(self):
        pe = PassengerElevator(0, 0, 20)
        # Add UP requests
        pe.add_request(1, 5)
        pe.add_request(3, 7)
        # Add DOWN request
        pe.add_request(10, 2)

        # First direction is UP (determined by first request)
        # UP requests should be processed first (sorted by origin ascending)
        r1 = pe.process_next()
        assert r1["origin"] == 1
        assert r1["destination"] == 5

        r2 = pe.process_next()
        assert r2["origin"] == 3
        assert r2["destination"] == 7

        # Now DOWN request
        r3 = pe.process_next()
        assert r3["origin"] == 10
        assert r3["destination"] == 2

        assert pe.get_pending_requests() == 0

    def test_directional_priority_down_first(self):
        pe = PassengerElevator(10, 0, 20)
        # First request is DOWN -> direction is DOWN
        pe.add_request(8, 2)
        pe.add_request(1, 6)  # UP request

        r1 = pe.process_next()
        assert r1["origin"] == 8  # DOWN processed first
        assert r1["destination"] == 2

        r2 = pe.process_next()
        assert r2["origin"] == 1  # Then UP
        assert r2["destination"] == 6

    def test_up_requests_sorted_ascending(self):
        pe = PassengerElevator(0, 0, 20)
        pe.add_request(5, 10)
        pe.add_request(1, 4)
        pe.add_request(3, 8)

        r1 = pe.process_next()
        assert r1["origin"] == 1  # lowest origin first

        r2 = pe.process_next()
        assert r2["origin"] == 3

        r3 = pe.process_next()
        assert r3["origin"] == 5

    def test_down_requests_sorted_descending(self):
        pe = PassengerElevator(15, 0, 20)
        pe.add_request(5, 1)
        pe.add_request(12, 3)
        pe.add_request(8, 2)

        r1 = pe.process_next()
        assert r1["origin"] == 12  # highest origin first

        r2 = pe.process_next()
        assert r2["origin"] == 8

        r3 = pe.process_next()
        assert r3["origin"] == 5

    def test_process_next_when_empty(self):
        pe = PassengerElevator(0, 0, 20)
        result = pe.process_next()
        assert result["origin"] is None
        assert result["destination"] is None

    def test_idle_after_all_processed(self):
        pe = PassengerElevator(0, 0, 20)
        pe.add_request(1, 5)
        pe.process_next()
        assert pe.get_state() == State.IDLE
        assert pe.get_pending_requests() == 0

    def test_ignore_same_floor_request(self):
        pe = PassengerElevator(0, 0, 20)
        pe.add_request(5, 5)
        assert pe.get_pending_requests() == 0

    def test_out_of_range_raises(self):
        pe = PassengerElevator(0, 0, 10)
        with pytest.raises(ValueError):
            pe.add_request(0, 15)
        with pytest.raises(ValueError):
            pe.add_request(-1, 5)


# ---------------------------------------------------------------------------
# Level 3: Service Elevator (FIFO)
# ---------------------------------------------------------------------------
class TestLevel3:
    def test_initial_state(self):
        se = ServiceElevator(0, 0, 20)
        assert se.get_state() == State.IDLE
        assert se.get_queue() == []

    def test_add_request(self):
        se = ServiceElevator(0, 0, 20)
        se.add_request(3, 7)
        assert len(se.get_queue()) == 1
        assert se.get_queue()[0] == (3, 7)

    def test_fifo_order(self):
        se = ServiceElevator(0, 0, 20)
        se.add_request(3, 7)
        se.add_request(1, 5)
        se.add_request(8, 2)

        r1 = se.process_next()
        assert r1["origin"] == 3
        assert r1["destination"] == 7

        r2 = se.process_next()
        assert r2["origin"] == 1
        assert r2["destination"] == 5

        r3 = se.process_next()
        assert r3["origin"] == 8
        assert r3["destination"] == 2

    def test_process_moves_to_origin_then_destination(self):
        se = ServiceElevator(0, 0, 20)
        se.add_request(5, 10)
        result = se.process_next()
        assert se.get_current_floor() == 10

    def test_process_next_when_empty(self):
        se = ServiceElevator(0, 0, 20)
        result = se.process_next()
        assert result["origin"] is None
        assert result["destination"] is None

    def test_idle_after_all_processed(self):
        se = ServiceElevator(0, 0, 20)
        se.add_request(1, 5)
        se.process_next()
        assert se.get_state() == State.IDLE

    def test_state_up_during_process(self):
        se = ServiceElevator(0, 0, 20)
        se.add_request(3, 8)
        se.add_request(1, 2)
        se.process_next()
        # After processing (3->8), floor is 8, next is (1,2)
        # State depends on remaining queue
        assert se.get_current_floor() == 8

    def test_state_down_request(self):
        se = ServiceElevator(10, 0, 20)
        se.add_request(8, 3)
        result = se.process_next()
        assert result["origin"] == 8
        assert result["destination"] == 3
        assert se.get_current_floor() == 3

    def test_queue_returns_copy(self):
        se = ServiceElevator(0, 0, 20)
        se.add_request(1, 5)
        q = se.get_queue()
        q.append((99, 99))
        assert len(se.get_queue()) == 1  # original not modified

    def test_multiple_requests_queue_length(self):
        se = ServiceElevator(0, 0, 20)
        for i in range(5):
            se.add_request(i, i + 5)
        assert len(se.get_queue()) == 5
        se.process_next()
        assert len(se.get_queue()) == 4

    def test_out_of_range_raises(self):
        se = ServiceElevator(0, 0, 10)
        with pytest.raises(ValueError):
            se.add_request(0, 15)
        with pytest.raises(ValueError):
            se.add_request(-1, 5)

    def test_fifo_not_sorted(self):
        """Verify FIFO order is maintained, not sorted by floor."""
        se = ServiceElevator(0, 0, 20)
        se.add_request(10, 15)
        se.add_request(2, 5)
        se.add_request(7, 1)

        r1 = se.process_next()
        assert r1["origin"] == 10  # first in, first out

        r2 = se.process_next()
        assert r2["origin"] == 2

        r3 = se.process_next()
        assert r3["origin"] == 7


# ---------------------------------------------------------------------------
# Level 4: Elevator System
# ---------------------------------------------------------------------------
class TestLevel4:
    def test_initial_status(self):
        system = ElevatorSystem(2, 1)
        status = system.get_status()
        assert "passenger_0" in status
        assert "passenger_1" in status
        assert "service_0" in status
        assert status["passenger_0"]["state"] == "IDLE"

    def test_dispatch_passenger_request(self):
        system = ElevatorSystem(1, 0)
        system.dispatch_request(1, 5, "passenger")
        status = system.get_status()
        assert status["passenger_0"]["pending"] == 1

    def test_dispatch_service_request(self):
        system = ElevatorSystem(0, 1)
        system.dispatch_request(1, 5, "service")
        status = system.get_status()
        assert status["service_0"]["pending"] == 1

    def test_dispatch_to_nearest_idle(self):
        system = ElevatorSystem(2, 0)
        # Move elevator 0 to floor 10 by processing a request
        system.passenger_elevators[0].add_request(0, 10)
        system.passenger_elevators[0].process_next()
        # Elevator 0 at floor 10, elevator 1 at floor 0
        # Request from floor 8 should go to elevator 0 (nearest)
        chosen = system.dispatch_request(8, 12, "passenger")
        assert chosen is system.passenger_elevators[0]

    def test_dispatch_to_least_loaded(self):
        system = ElevatorSystem(2, 0)
        # Load up elevator 0
        system.passenger_elevators[0].add_request(1, 5)
        system.passenger_elevators[0].add_request(2, 6)
        # Elevator 1 has no requests
        # Both are idle initially, but elevator 0 gets requests making it non-idle
        # After first add_request, elevator 0 gets direction set
        # Elevator 1 is still idle -> nearest idle wins
        chosen = system.dispatch_request(3, 7, "passenger")
        # Elevator 1 is idle, so it should be chosen
        assert chosen is system.passenger_elevators[1]

    def test_process_all_passenger(self):
        system = ElevatorSystem(1, 0)
        system.dispatch_request(1, 5, "passenger")
        system.dispatch_request(3, 8, "passenger")
        results = system.process_all()
        assert len(results["passenger"]) == 2
        assert results["service"] == []

    def test_process_all_service(self):
        system = ElevatorSystem(0, 1)
        system.dispatch_request(1, 5, "service")
        system.dispatch_request(3, 8, "service")
        results = system.process_all()
        assert len(results["service"]) == 2
        assert results["passenger"] == []

    def test_process_all_mixed(self):
        system = ElevatorSystem(1, 1)
        system.dispatch_request(1, 5, "passenger")
        system.dispatch_request(3, 8, "service")
        results = system.process_all()
        assert len(results["passenger"]) == 1
        assert len(results["service"]) == 1

    def test_invalid_elevator_type(self):
        system = ElevatorSystem(1, 1)
        with pytest.raises(ValueError):
            system.dispatch_request(1, 5, "freight")

    def test_status_after_processing(self):
        system = ElevatorSystem(1, 1)
        system.dispatch_request(1, 5, "passenger")
        system.dispatch_request(3, 8, "service")
        system.process_all()
        status = system.get_status()
        assert status["passenger_0"]["state"] == "IDLE"
        assert status["passenger_0"]["pending"] == 0
        assert status["service_0"]["state"] == "IDLE"
        assert status["service_0"]["pending"] == 0

    def test_multiple_dispatches_to_same_type(self):
        system = ElevatorSystem(2, 0)
        # Both start idle at floor 0, first dispatch goes to nearest (both equidistant, picks first)
        system.dispatch_request(1, 5, "passenger")
        # Now elevator 0 has a request (direction set), elevator 1 is idle
        system.dispatch_request(2, 6, "passenger")
        # Elevator 1 is idle, should get the second request
        assert system.passenger_elevators[0].get_pending_requests() == 1
        assert system.passenger_elevators[1].get_pending_requests() == 1

    def test_get_status_floor_updates(self):
        system = ElevatorSystem(0, 1)
        system.dispatch_request(0, 15, "service")
        system.process_all()
        status = system.get_status()
        assert status["service_0"]["floor"] == 15
