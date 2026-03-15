# Elevator System Design

An ICF-style system design project based on the NeetCode Elevator design pattern.

## Core Concepts

- **State**: `IDLE`, `UP`, `DOWN`
- **Elevator Types**: `PassengerElevator` (directional priority), `ServiceElevator` (FIFO)
- **Request Types**: `INSIDE` (destination only), `OUTSIDE` (origin + destination)

## Level Specifications

### Level 1: Basic Elevator

Class: `Elevator(current_floor, min_floor, max_floor)`

A single elevator that serves requests in the order they are received.

**Methods:**
- `request(destination_floor)` — add a destination to the queue
- `step()` — move the elevator one floor toward the next destination; returns current floor
- `get_state()` — returns `State.IDLE`, `State.UP`, or `State.DOWN`
- `get_current_floor()` — returns the current floor as an int

**Behavior:** Requests are served in FIFO order. The elevator moves one floor per `step()` call. Once a destination is reached, the next request is dequeued.

### Level 2: Passenger Elevator (Directional Priority)

Class: `PassengerElevator(current_floor, min_floor, max_floor)`

Extends `Elevator` with directional priority scheduling.

**Methods:**
- `add_request(origin_floor, destination_floor)` — add an outside request (origin + destination)
- `process_next()` — process the next request in the current direction; returns a dict with state info
- `get_pending_requests()` — returns the count of pending requests

**Behavior:** Processes all requests in the current direction before switching. Uses sorted lists: ascending for UP requests, descending for DOWN requests. Direction is determined by the first request if idle.

### Level 3: Service Elevator (FIFO)

Class: `ServiceElevator(current_floor, min_floor, max_floor)`

Extends `Elevator` with strict FIFO request processing.

**Methods:**
- `add_request(origin_floor, destination_floor)` — add a request to the FIFO queue
- `process_next()` — process the next request in FIFO order; returns a dict with state info
- `get_queue()` — returns a list of pending requests as `(origin, destination)` tuples

**Behavior:** Requests are processed in exactly the order they were added. The elevator first moves to the origin floor, picks up, then moves to the destination floor.

### Level 4: Elevator System

Class: `ElevatorSystem(num_passenger, num_service)`

Manages a fleet of passenger and service elevators.

**Methods:**
- `dispatch_request(origin, destination, elevator_type)` — dispatch to the nearest idle elevator, or the least-loaded elevator if none are idle
- `get_status()` — returns a dict with each elevator's state and current floor
- `process_all()` — processes all pending requests across all elevators; returns a summary dict

**Dispatch Strategy:** Prefer the nearest idle elevator. If no idle elevator of the requested type exists, dispatch to the one with the fewest pending requests.
