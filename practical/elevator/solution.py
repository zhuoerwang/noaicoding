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
        self.current_floor = current_floor
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.state = State.IDLE
        self.destinations = deque()

    def request(self, destination_floor: int):
        if destination_floor < self.min_floor or destination_floor > self.max_floor:
            raise ValueError(
                f"Floor {destination_floor} out of range [{self.min_floor}, {self.max_floor}]"
            )
        self.destinations.append(destination_floor)
        self._update_state()

    def step(self) -> int:
        if self.state == State.IDLE:
            return self.current_floor

        target = self.destinations[0]

        if self.current_floor < target:
            self.current_floor += 1
        elif self.current_floor > target:
            self.current_floor -= 1

        if self.current_floor == target:
            self.destinations.popleft()
            self._update_state()

        return self.current_floor

    def _update_state(self):
        if not self.destinations:
            self.state = State.IDLE
        elif self.destinations[0] > self.current_floor:
            self.state = State.UP
        elif self.destinations[0] < self.current_floor:
            self.state = State.DOWN
        else:
            # Already at the destination, pop it and recalculate
            self.destinations.popleft()
            self._update_state()

    def get_state(self) -> State:
        return self.state

    def get_current_floor(self) -> int:
        return self.current_floor


# ---------------------------------------------------------------------------
# Level 2: Passenger Elevator (Directional Priority)
# ---------------------------------------------------------------------------
class PassengerElevator(Elevator):
    def __init__(self, current_floor: int, min_floor: int, max_floor: int):
        super().__init__(current_floor, min_floor, max_floor)
        self.up_requests = []      # sorted ascending by origin
        self.down_requests = []    # sorted descending by origin (highest first)
        self.direction = None      # 'up' or 'down' or None

    def add_request(self, origin_floor: int, destination_floor: int):
        if origin_floor < self.min_floor or origin_floor > self.max_floor:
            raise ValueError(f"Origin floor {origin_floor} out of range")
        if destination_floor < self.min_floor or destination_floor > self.max_floor:
            raise ValueError(f"Destination floor {destination_floor} out of range")

        if destination_floor > origin_floor:
            # This is an UP request
            self.up_requests.append((origin_floor, destination_floor))
            self.up_requests.sort(key=lambda r: r[0])
        elif destination_floor < origin_floor:
            # This is a DOWN request
            self.down_requests.append((origin_floor, destination_floor))
            self.down_requests.sort(key=lambda r: -r[0])
        else:
            return  # origin == destination, ignore

        if self.direction is None:
            if destination_floor > origin_floor:
                self.direction = "up"
                self.state = State.UP
            else:
                self.direction = "down"
                self.state = State.DOWN

    def process_next(self) -> dict:
        if not self.up_requests and not self.down_requests:
            self.direction = None
            self.state = State.IDLE
            return {"origin": None, "destination": None, "direction": None}

        # Pick the direction: prefer current direction, switch if empty
        if self.direction == "up" and not self.up_requests:
            self.direction = "down"
        elif self.direction == "down" and not self.down_requests:
            self.direction = "up"
        elif self.direction is None:
            self.direction = "up" if self.up_requests else "down"

        if self.direction == "up":
            origin, destination = self.up_requests.pop(0)
            self.state = State.UP
        else:
            origin, destination = self.down_requests.pop(0)
            self.state = State.DOWN

        # Move to origin
        self.current_floor = origin
        # Move to destination
        self.current_floor = destination

        if not self.up_requests and not self.down_requests:
            self.state = State.IDLE
            self.direction = None

        return {
            "origin": origin,
            "destination": destination,
            "direction": self.direction if self.direction else ("up" if destination > origin else "down"),
        }

    def get_pending_requests(self) -> int:
        return len(self.up_requests) + len(self.down_requests)


# ---------------------------------------------------------------------------
# Level 3: Service Elevator (FIFO)
# ---------------------------------------------------------------------------
class ServiceElevator(Elevator):
    def __init__(self, current_floor: int, min_floor: int, max_floor: int):
        super().__init__(current_floor, min_floor, max_floor)
        self.request_queue = deque()

    def add_request(self, origin_floor: int, destination_floor: int):
        if origin_floor < self.min_floor or origin_floor > self.max_floor:
            raise ValueError(f"Origin floor {origin_floor} out of range")
        if destination_floor < self.min_floor or destination_floor > self.max_floor:
            raise ValueError(f"Destination floor {destination_floor} out of range")
        self.request_queue.append((origin_floor, destination_floor))

    def process_next(self) -> dict:
        if not self.request_queue:
            self.state = State.IDLE
            return {"origin": None, "destination": None}

        origin, destination = self.request_queue.popleft()

        # Move to origin
        if origin > self.current_floor:
            self.state = State.UP
        elif origin < self.current_floor:
            self.state = State.DOWN
        self.current_floor = origin

        # Move to destination
        if destination > self.current_floor:
            self.state = State.UP
        elif destination < self.current_floor:
            self.state = State.DOWN
        self.current_floor = destination

        if not self.request_queue:
            self.state = State.IDLE

        return {"origin": origin, "destination": destination}

    def get_queue(self) -> list:
        return list(self.request_queue)


# ---------------------------------------------------------------------------
# Level 4: Elevator System
# ---------------------------------------------------------------------------
class ElevatorSystem:
    def __init__(self, num_passenger: int, num_service: int, min_floor: int = 0, max_floor: int = 20):
        self.passenger_elevators = [
            PassengerElevator(0, min_floor, max_floor) for _ in range(num_passenger)
        ]
        self.service_elevators = [
            ServiceElevator(0, min_floor, max_floor) for _ in range(num_service)
        ]
        self.min_floor = min_floor
        self.max_floor = max_floor

    def _get_elevators(self, elevator_type: str) -> list:
        if elevator_type == "passenger":
            return self.passenger_elevators
        elif elevator_type == "service":
            return self.service_elevators
        else:
            raise ValueError(f"Unknown elevator type: {elevator_type}")

    def _get_load(self, elevator) -> int:
        if isinstance(elevator, PassengerElevator):
            return elevator.get_pending_requests()
        elif isinstance(elevator, ServiceElevator):
            return len(elevator.get_queue())
        return 0

    def dispatch_request(self, origin: int, destination: int, elevator_type: str):
        elevators = self._get_elevators(elevator_type)
        if not elevators:
            raise ValueError(f"No {elevator_type} elevators available")

        # Find nearest idle elevator
        best_idle = None
        best_idle_dist = float("inf")
        for elev in elevators:
            if elev.get_state() == State.IDLE:
                dist = abs(elev.get_current_floor() - origin)
                if dist < best_idle_dist:
                    best_idle = elev
                    best_idle_dist = dist

        if best_idle is not None:
            chosen = best_idle
        else:
            # Find least-loaded elevator
            chosen = min(elevators, key=lambda e: self._get_load(e))

        if isinstance(chosen, PassengerElevator):
            chosen.add_request(origin, destination)
        else:
            chosen.add_request(origin, destination)

        return chosen

    def get_status(self) -> dict:
        status = {}
        for i, elev in enumerate(self.passenger_elevators):
            status[f"passenger_{i}"] = {
                "state": elev.get_state().value,
                "floor": elev.get_current_floor(),
                "pending": elev.get_pending_requests(),
            }
        for i, elev in enumerate(self.service_elevators):
            status[f"service_{i}"] = {
                "state": elev.get_state().value,
                "floor": elev.get_current_floor(),
                "pending": len(elev.get_queue()),
            }
        return status

    def process_all(self) -> dict:
        results = {"passenger": [], "service": []}

        for elev in self.passenger_elevators:
            while elev.get_pending_requests() > 0:
                result = elev.process_next()
                results["passenger"].append(result)

        for elev in self.service_elevators:
            while elev.get_queue():
                result = elev.process_next()
                results["service"].append(result)

        return results
