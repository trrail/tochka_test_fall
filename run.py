import sys
import heapq

ENERGY_COST = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
ROOM_ENTER_POSITIONS = [2, 4, 6, 8]
POSITIONS_TO_STOP_IN_HALL = [0, 1, 3, 5, 7, 9, 10]
ROOMS_COUNT = 4
LETTER_SYMBOLS = "ABCD"
EMPTY_SYMBOL = "."
LETTER_A_ASCII_CODE = 65
HALL_LENGTH = 11

def heuristic(state, depth):
    hall_positions_state, rooms_positions_state = state.split("|")
    total_minimal_energy = 0
    for i, hall_position in enumerate(hall_positions_state):
        if hall_position in LETTER_SYMBOLS:
            goal_room_for_ampiphode = ROOM_ENTER_POSITIONS[ord(hall_position) - 65]
            total_minimal_energy += (abs(i - goal_room_for_ampiphode) + 1) * ENERGY_COST[hall_position]
    for room_idx in range(ROOMS_COUNT):
        room = rooms_positions_state[room_idx * depth:(room_idx + 1) * depth]
        for depth_idx, hall_position in enumerate(room):
            if hall_position in LETTER_SYMBOLS:
                ampiphode_room_index = ord(hall_position) - LETTER_A_ASCII_CODE
                if ampiphode_room_index != room_idx:
                    total_minimal_energy += ((abs(ROOM_ENTER_POSITIONS[room_idx] -
                                                 ROOM_ENTER_POSITIONS[ampiphode_room_index]) + depth_idx + 2)
                                             * ENERGY_COST[hall_position])
    return total_minimal_energy

def get_moves(labyrinth_state_code, rooms_depth):
    hall_positions_state, rooms_positions_state = labyrinth_state_code.split("|")
    hall_positions_state = list(hall_positions_state)
    rooms_list = [rooms_positions_state[i * rooms_depth:(i + 1) * rooms_depth] for i in range(ROOMS_COUNT)]
    moves = []

    # Ходы из коридора в комнату
    for i, hall_symbol in enumerate(hall_positions_state):
        if hall_symbol not in LETTER_SYMBOLS:
            continue
        goal_room_to_ampiphode = ord(hall_symbol) - LETTER_A_ASCII_CODE
        entrance_pos_to_goal_room = ROOM_ENTER_POSITIONS[goal_room_to_ampiphode]
        left_border, right_border = sorted([i, entrance_pos_to_goal_room])
        if any(hall_positions_state[pos] != EMPTY_SYMBOL for pos in range(left_border + 1, right_border)):
            continue
        room = rooms_list[goal_room_to_ampiphode]
        if any(room_symbol != EMPTY_SYMBOL and room_symbol != hall_symbol for room_symbol in room):
            continue
        deepest_room_free_pos = None
        for room_pos in range(rooms_depth - 1, -1, -1):
            if room[room_pos] == EMPTY_SYMBOL:
                deepest_room_free_pos = room_pos
                break
        if deepest_room_free_pos is not None:
            steps_to_free_pos = abs(i - entrance_pos_to_goal_room) + deepest_room_free_pos + 1
            energy_cost_to_free_pos = steps_to_free_pos * ENERGY_COST[hall_symbol]
            new_hall_positions_state = hall_positions_state.copy()
            new_hall_positions_state[i] = EMPTY_SYMBOL
            new_rooms = rooms_list.copy()
            room = list(room)
            room[deepest_room_free_pos] = hall_symbol
            new_rooms[goal_room_to_ampiphode] = "".join(room)
            moves.append(("".join(new_hall_positions_state) + "|" + "".join(new_rooms), energy_cost_to_free_pos))

    if moves:
        return moves

    # Ходы из комнаты в коридор
    for i in range(ROOMS_COUNT):
        room = list(rooms_list[i])
        top_ampiphode_idx = next((i for i, c in enumerate(room) if c != EMPTY_SYMBOL), None)
        if top_ampiphode_idx is None:
            continue
        hall_symbol = room[top_ampiphode_idx]
        if hall_symbol == chr(LETTER_A_ASCII_CODE + i) and all(x == hall_symbol for x in room[top_ampiphode_idx:]):
            continue
        entrance_pos_to_goal_room = ROOM_ENTER_POSITIONS[i]
        # Влево
        for pos in range(entrance_pos_to_goal_room - 1, -1, -1):
            if hall_positions_state[pos] != EMPTY_SYMBOL:
                break
            if pos in POSITIONS_TO_STOP_IN_HALL:
                steps_to_free_pos = top_ampiphode_idx + 1 + abs(entrance_pos_to_goal_room - pos)
                energy_cost_to_free_pos = steps_to_free_pos * ENERGY_COST[hall_symbol]
                new_hall_positions_state = hall_positions_state.copy()
                new_hall_positions_state[pos] = hall_symbol
                new_rooms = rooms_list.copy()
                room[top_ampiphode_idx] = EMPTY_SYMBOL
                new_rooms[i] = "".join(room)
                moves.append(("".join(new_hall_positions_state) + "|" + "".join(new_rooms), energy_cost_to_free_pos))
        # Вправо
        for pos in range(entrance_pos_to_goal_room + 1, HALL_LENGTH):
            if hall_positions_state[pos] != EMPTY_SYMBOL:
                break
            if pos in POSITIONS_TO_STOP_IN_HALL:
                steps_to_free_pos = top_ampiphode_idx + 1 + abs(entrance_pos_to_goal_room - pos)
                energy_cost_to_free_pos = steps_to_free_pos * ENERGY_COST[hall_symbol]
                new_hall_positions_state = hall_positions_state.copy()
                new_hall_positions_state[pos] = hall_symbol
                new_rooms = rooms_list.copy()
                room[top_ampiphode_idx] = EMPTY_SYMBOL
                new_rooms[i] = "".join(room)
                moves.append(("".join(new_hall_positions_state) + "|" + "".join(new_rooms), energy_cost_to_free_pos))
    return moves

def a_star(labyrinth_start_code, goal_rooms_state, room_depth):
    queue = []
    heapq.heappush(queue, (heuristic(labyrinth_start_code, room_depth), 0, labyrinth_start_code))
    minimal_energy_cost_for_state = {labyrinth_start_code: 0}

    while queue:
        _, accumulated_energy, current_labyrinth_state = heapq.heappop(queue)
        if minimal_energy_cost_for_state.get(current_labyrinth_state, 10**9) < accumulated_energy:
            continue
        hall_state, rooms_state = current_labyrinth_state.split("|")
        if rooms_state == goal_rooms_state:
            return accumulated_energy
        for new_state, move_energy_cost in get_moves(current_labyrinth_state, room_depth):
            new_energy_cost = accumulated_energy + move_energy_cost
            if new_energy_cost < minimal_energy_cost_for_state.get(new_state, 10**9):
                minimal_energy_cost_for_state[new_state] = new_energy_cost
                heapq.heappush(queue, (new_energy_cost + heuristic(new_state, room_depth),
                                       new_energy_cost, new_state))
    return 0

def solve(lines: list[str]) -> int:
    hall = list(lines[1][1:HALL_LENGTH + 1])
    room_lines = [line[3:10:2] for line in lines[2:-1]]
    room_depth = len(room_lines)
    rooms = []
    for r in range(ROOMS_COUNT):
        col = "".join(room_lines[i][r] for i in range(room_depth))
        rooms.append(col)
    hall = [EMPTY_SYMBOL if c not in LETTER_SYMBOLS else c for c in hall]
    rooms = ["".join(EMPTY_SYMBOL if c not in LETTER_SYMBOLS else c for c in room) for room in rooms]

    labyrinth_state_code = "".join(hall) + "|" + "".join(rooms)
    goal_rooms_state = "".join("".join(chr(LETTER_A_ASCII_CODE + i) * room_depth for i in range(4)))

    result = a_star(labyrinth_state_code, goal_rooms_state, room_depth)
    return result

def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip("\n"))

    print(solve(lines))

if __name__ == "__main__":
    main()
