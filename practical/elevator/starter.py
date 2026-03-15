from enum import Enum
from collections import deque


class State(Enum):
    IDLE = "IDLE"
    UP = "UP"
    DOWN = "DOWN"


# ---------------------------------------------------------------------------
# Level 1: Basic Elevator
# ---------------------------------------------------------------------------
class Elevator:
    def __init__(self, current_floor: int, min_floor: int, max_floor: int):
        pass

    def request(self, destination_floor: int):
        """Add a destination floor to the request queue."""
        pass

    def step(self) -> int:
        """Move one floor toward the next destination. Returns current floor."""
        pass

    def get_state(self) -> State:
        """Return the current state: IDLE, UP, or DOWN."""
        pass

    def get_current_floor(self) -> int:
        """Return the current floor number."""
        pass


# ---------------------------------------------------------------------------
# Level 2: Passenger Elevator (Directional Priority)
# ---------------------------------------------------------------------------
class PassengerElevator(Elevator):
    def __init__(self, current_floor: int, min_floor: int, max_floor: int):
        pass

    def add_request(self, origin_floor: int, destination_floor: int):
        """Add an outside request with origin and destination."""
        pass

    def process_next(self) -> dict:
        """Process the next request in the current direction.
        Returns a dict with keys: 'origin', 'destination', 'direction'."""
        pass

    def get_pending_requests(self) -> int:
        """Return the count of all pending requests."""
        pass


# ---------------------------------------------------------------------------
# Level 3: Service Elevator (FIFO)
# ---------------------------------------------------------------------------
class ServiceElevator(Elevator):
    def __init__(self, current_floor: int, min_floor: int, max_floor: int):
        pass

    def add_request(self, origin_floor: int, destination_floor: int):
        """Add a request to the FIFO queue."""
        pass

    def process_next(self) -> dict:
        """Process the next request in FIFO order.
        Returns a dict with keys: 'origin', 'destination'."""
        pass

    def get_queue(self) -> list:
        """Return a list of pending requests as (origin, destination) tuples."""
        pass


# ---------------------------------------------------------------------------
# Level 4: Elevator System
# ---------------------------------------------------------------------------
class ElevatorSystem:
    def __init__(self, num_passenger: int, num_service: int):
        pass

    def dispatch_request(self, origin: int, destination: int, elevator_type: str):
        """Dispatch a request to the nearest idle elevator of the given type,
        or the least-loaded if none are idle.
        elevator_type is 'passenger' or 'service'."""
        pass

    def get_status(self) -> dict:
        """Return a dict with each elevator's state and current floor."""
        pass

    def process_all(self) -> dict:
        """Process all pending requests across all elevators.
        Returns a summary dict."""
        pass
