#TODO winning condition where player is stuck
#TODO unit tests
#TODO SmartestRandomPlayer that moves up whenever possible???
#TODO improve DEBUG
#TODO calling worker_locations over and over again slow?

DEBUG = False

import random

class RulesError(RuntimeError):
    pass

class worker:
    def __init__(self, code):
        self.code = code
        
    def __repr__(self):
        return "worker('{}')".format(self.code)
    
    def __str__(self):
        return self.code

class BoardSpace:
    def __init__(self, board, x, y):
        self.block_level = 0
        self.worker = None
        self.board = board
        self.x = x
        self.y = y
        
    def coords(self):
        return (self.x, self.y)

    def is_domed(self):
        return self.block_level == 4
    
    def is_occupied(self):
        return self.worker is not None
    
    def is_open(self):
        return not self.is_occupied() and not self.is_domed()
    
    def is_winner(self):
        return self.is_occupied() and self.block_level == 3
        
    def add_worker(self, worker):
        if self.is_domed():
            raise RulesError("Can't move a worker here; space is domed")
        elif self.is_occupied():
            raise RulesError("Can't move a worker here; space is already occupied")
        else:
            self.worker = worker
            
    def remove_worker(self):
        if not self.is_occupied():
            raise RulesError("No worker to remove from this space")
        else:
            self.worker = None
               
    def add_block(self):
        if self.is_domed():
            raise RulesError("Can't add a block; space is already domed")
        elif self.is_occupied():
            raise RulesError("Can't add a block; space is occupied")
        else:
            self.block_level += 1
            
    def move(self, new_space):
        if self.is_occupied() and new_space in self.available_moves():
            worker = self.worker
            self.remove_worker()
            new_space.add_worker(worker)
        elif not self.is_occupied():
            raise RulesError("No worker to move from this space")
        else:
            raise RulesError("worker cannot move to that space")
            
        if DEBUG: self.board.show()
        #print("{} moved to {}".format(new_space.worker.code, new_space.coords))
            
    def build(self, build_space):
        if self.is_occupied() and build_space in self.available_builds():
            build_space.add_block()
        elif not self.is_occupied():
            raise RulesError("No worker to build with on this space")
        else:
            raise RulesError("worker cannot build on that space")
            
        if DEBUG: self.board.show()
        #print("{} built on {}".format(self.worker.code, build_space.coords))

    def adjacent_spaces(self):
        return self.board.adjacent_spaces(self.x, self.y)
    
    def available_moves(self):
        if self.is_occupied():
            return [
                space for space in self.adjacent_spaces() 
                if space.is_open() and space.block_level <= self.block_level + 1
            ]
        else:
            return None
        
    def available_builds(self):
        if self.is_occupied():
            return [
                space for space in self.adjacent_spaces() 
                if not space.is_occupied() and not space.is_domed()
            ]
        else:
            return None
        
    def __repr__(self):
        return "BoardSpace({}, {}, {})".format(repr(self.board), self.x, self.y)
    
    def __str__(self):
        worker_char = self.worker if self.is_occupied() else ' '
        if self.block_level == 0:
            block_char = ' '
        elif self.block_level == 4:
            block_char = 'D'
        else:
            block_char = self.block_level
        return "[{} {}]".format(block_char, worker_char)
    
class Board:
    def __init__(self, x_spaces, y_spaces):
        self._spaces = [[BoardSpace(self, x, y) for y in range(y_spaces)] for x in range(x_spaces)]
        self.x_max = x_spaces - 1
        self.y_max = y_spaces - 1
        
    def dimensions(self):
        return (self.x_max + 1, self.y_max + 1)
    
    def __getitem__(self, key):
        if key[0] < 0 or key[1] < 0:
            raise IndexError('cannot pass negative values')
        if key[0] > self.x_max or key[1] > self.y_max:
            raise IndexError('value does not exist on board')
        return self._spaces[key[0]][key[1]]
    
    def __setitem__(self, key, value):
        self._spaces[key] = value
        
    def worker_locations(self):
        locs = {}
        for row in self._spaces:
            for space in row:
                if space.is_occupied():
                    locs[space.worker.code] = space 
        return locs
    
    def adjacent_spaces(self, x, y):
        adj_coords = [
            (x-1, y-1), (x-1, y), (x-1, y+1),
            (x,   y-1),           (x,   y+1),
            (x+1, y-1), (x+1, y), (x+1, y+1)
        ]
        adj_spaces = []
        for x, y in adj_coords:
            try:
                adj_spaces.append(self[x,y])
            except IndexError: # past edge of board
                pass
        return adj_spaces
    
    def __repr__(self):
        return "Board({}, {})".format(self.x_max + 1, self.y_max + 1)
    
    def __str__(self):
        s = ''
        for row in self._spaces:
            for space in row:
                s += str(space)
            s += '\n'
        return s  

    def show(self):
        print(str(self))    
    
class Game:
    def __init__(self, player1, player2, board_dimensions=(5,5)):
        self.board = Board(*board_dimensions)
        self.players = (player1, player2)

    def players(self):
        return [0, 1]
        
    def set_initial_position(self, player, worker_num, pos):
        x, y = pos
        self.board[x, y].add_worker(self.players[player].workers[worker_num])
    
    def winning_worker(self):
        for player in self.players:
            for worker in player.workers:
                if self.board.worker_locations()[worker.code].is_winner():
                    return worker
        return None
    
    def is_complete(self):
        if self.winning_worker() is not None:
            return True

        return False

class Player:
    def __init__(self, worker1, worker2):
        self.workers = (worker1, worker2)

    def take_turn(self, board):
        pass

class RandomPlayer(Player):
    def take_turn(self, board):
        worker_locations = board.worker_locations()

        # Select a worker to use at random
        worker_num = random.randint(0, 1)
        worker = self.workers[worker_num]
        original_space = worker_locations[worker.code]
        available_moves = original_space.available_moves()

        if len(available_moves) == 0:
            # Use the other worker
            worker_num = 1 if worker_num == 0 else 0
            worker = self.workers[worker_num]
            original_space = worker_locations[worker.code]
            available_moves = original_space.available_moves()

        # Choose a random move for this worker
        new_space = random.choice(available_moves)
        original_space.move(new_space)
        
        # Choose a random build for this worker
        new_space.build(random.choice(new_space.available_builds()))

class SmarterRandomPlayer(RandomPlayer):
    def take_turn(self, board):
        worker_locations = board.worker_locations()

        new_space = None
        for worker in self.workers:
            original_space = worker_locations[worker.code]
            available_moves = original_space.available_moves()
            
            # If there is immediately winning move, make it
            for space in available_moves:
                if space.block_level == 3:
                    new_space = space
                    original_space.move(new_space)
                    return

        if not new_space:
            RandomPlayer.take_turn(self, board)


def simulate_random_game(player_type1, player_type2):
    g = Game(
        player1=player_type1(worker('O'), worker('o')),
        player2=player_type2(worker('X'), worker('x')),
    )

    g.set_initial_position(0, 0, (1, 1))
    g.set_initial_position(1, 0, (1, 3))
    g.set_initial_position(0, 1, (3, 3))
    g.set_initial_position(1, 1, (3, 1))

    current_player = 0
    turn_num = 0
    while not g.is_complete():
        turn_num += 1
        g.players[current_player].take_turn(g.board)
        current_player = 1 if current_player == 0 else 0
    return g.winning_worker().code, turn_num, g.board