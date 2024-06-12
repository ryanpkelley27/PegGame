import math
import copy

#settings
HUMAN_PLAYER = True
EMPTY_SPACE = 0#[0,14]

#constants
BOARD_SIZE = 15

class Game:
    global BOARD_SIZE
    board = []
    occupied = "T"
    empty = "O"
    #all moves
    #key is the peg that's moving, value is a dictionary where the key is the location the peg is moving to and the value is the peg that's being jumped
    moves = {0:{3:1,5:2}, 1:{6:3,8:4}, 2:{7:4,9:5}, 3:{0:1,5:4,10:6,12:7}, 4:{11:7,13:8}, 
             5:{0:2,3:4,12:8,14:9}, 6:{1:3,8:7}, 7:{2:4,9:8}, 8:{1:4,6:7}, 9:{2:5,7:8},
             10:{3:6,12:11}, 11:{4:7,13:12}, 12:{3:7,5:8,10:11,14:13}, 13:{4:8,11:12}, 14:{5:9,12:13}}

    def __init__(self, empty=0, board=None):
        if board==None:
            self.board = [self.occupied for i in range(BOARD_SIZE)]
            self.board[empty] = self.empty
        else:
            self.board = copy.deepcopy(board)

    def print(self):
        print()
        print("     %c"%self.board[0])
        print("    %c %c"%(self.board[1], self.board[2]))
        print("   %c %c %c"%(self.board[3], self.board[4],self.board[5]))
        print("  %c %c %c %c"%(self.board[6], self.board[7], self.board[8], self.board[9]))
        print(" %c %c %c %c %c"%(self.board[10],self.board[11],self.board[12],self.board[13],self.board[14]))
        print()

    def print_help(self):
        print("JUMP ALL BUT ONE GAMES")
        print("JUMP EACH TEE AND REMOVE IT")
        print("LEAVE ONLY ONE-YOU'RE GENIUS")
        print("LEAVE TWO AND YOU'RE PURTY SMART")
        print("LEAVE THREE AND YOU'RE JUST PLAIN DUMB")
        print("LEAVE FOUR OR MOR'N YOU'RE JUST PLAIN \"EG-NO-RA-MOOSE\"")
        print("Example input: ")
        print("Enter a peg to move and a space to move it to separated by a space: 3 0")
        print()
        print("        %d"%0)
        print("      %d  %d"%(1, 2))
        print("     %d  %d  %d"%(3, 4, 5))
        print("   %d  %d  %d  %d"%(6, 7, 8, 9))
        print(" %d %d %d %d %d"%(10,11,12,13,14))
        print()

    #only needed if you limit depth
    def static_score(self):
        global BOARD_SIZE
        score = 0
        number_of_pegs = 0
        for p in self.board:
            if p == self.occupied:
                number_of_pegs += 1

        if number_of_pegs == 1:
            return math.inf
        else:
            return BOARD_SIZE - number_of_pegs -1

    def is_legal(self, a,b, print_error=True):
        global BOARD_SIZE
        if a < 0 or a >= BOARD_SIZE:
            if print_error:
                print("Peg location does not exist: %d"%a)
            return False
        if b < 0 or b >= BOARD_SIZE:
            if print_error:
                print("Peg location does not exist: %d"%b)
            return False
        if self.board[a] != self.occupied:
            if print_error:
                print("Peg does not exist at %d"%a)
            return False
        if self.board[b] == self.occupied:
            if print_error:
                print("Peg is blocking a move to %d"%b)
            return False
        if not b in self.moves[a]:
            if print_error:
                print("Peg can't move there")
            return False
        if self.board[self.moves[a][b]] != self.occupied:
            if print_error:
                print("Peg needs another peg to jump over at %d"%self.moves[a][b])
            return False
        return True

    #move piece from a to b, returns true if move was successfully made, false otherwise
    def make_move(self, a, b, print_error=True):
        if self.is_legal(a,b, print_error):
            self.board[a] = self.empty
            self.board[b] = self.occupied
            self.board[self.moves[a][b]] = self.empty
            return True
        else:
            return False

    #returns the nnumber of pegs left after game end or None if there are still moves to be made
    def check_end(self):
        pegs = 0
        for i in range(BOARD_SIZE):
           if self.board[i] == self.occupied:
               pegs+=1
           for m in self.moves[i]:#iterate over moves: i->m
               if self.is_legal(i,m, False):
                   return None
        return pegs

    #returns number of pegs in board
    def count_pegs(self):
        global BOARD_SIZE
        count = 0
        for i in range(BOARD_SIZE):
            if self.board[i] == self.occupied:
                count += 1
        return count

    #returns two ints representing a moves
    def get_human_move(self):
        global BOARD_SIZE
        str = input("Enter a peg to move and a space to move it to separated by a space: ")
        list = str.split()

        if len(list) == 1 and list[0]=="help":
            game.print_help()
            game.print()
            return None, None


        if len(list) != 2:
            print("Enter only two numbers.")
            return None, None
        else:
            try:
                a = int(list[0])
                b = int(list[1])
            except Exception:
                return None, None
            if not self.is_legal(a,b):
                return None, None
        return a,b

    # deterministic? - [[3, 0], [5, 3], [0, 5], [6, 1], [9, 2], [11, 4], [12, 5], [1, 8], [2, 9], [14, 5], [5, 12], [13, 11], [10, 12]] for empty=0
    #returns sequence of moves
    def get_ai_sequence(self):
        global BOARD_SIZE
        best_score = -math.inf
        best_seq = []

        for a in range(BOARD_SIZE):
            print("At %d out of %d"%(a+1,BOARD_SIZE))
            if self.board[a]==self.occupied:
                for b in self.moves[a]:
                    _game = Game(board=self.board)
                    if not _game.make_move(a,b, False):
                        continue
                    seq = []
                    seq.append([a,b])

                    score, seq = _game._ai(seq)
                    if score > best_score:
                        best_score = score
                        best_seq = copy.deepcopy(seq)

        return best_seq

    def _ai(self, seq, depth=0):
        #print("Depth: %d"%depth)
        if depth>13: # all games end in 13 moves or less
            print("Error: ai went too deep")
            return 0, seq
        global BOARD_SIZE

        #base case - game end
        pegs_left = self.check_end()
        if pegs_left != None:
            if pegs_left == 1:
                return math.inf, seq
            else:
                return BOARD_SIZE - pegs_left - 1, seq

        #recursive case
        best_score = -math.inf
        best_seq = []
        for a in range(BOARD_SIZE):
            if self.board[a]==self.occupied:
                for b in self.moves[a]:
                    _game = Game(board=self.board)
                    if not _game.make_move(a,b, False):
                        continue
                    _seq = copy.deepcopy(seq)
                    _seq.append([a,b])

                    score, _seq = _game._ai(_seq, depth+1)
                    if score > best_score:
                        best_score = score
                        best_seq = copy.deepcopy(_seq)
                        if best_score == math.inf:
                            break
            if best_score==math.inf:
                break
        return best_score, best_seq


game = Game(empty=EMPTY_SPACE)
a = None
b = None
seq = None
pegs_left = BOARD_SIZE - 1
playing = True
game.print_help()
while playing:
    game.print()
    if HUMAN_PLAYER:
        a,b = game.get_human_move()
        while a==None:
            a,b = game.get_human_move()
        game.make_move(a,b)
    else:
        seq = game.get_ai_sequence()
        #print(seq)
        for i in range(len(seq)):
            game.make_move(seq[i][0], seq[i][1])
            game.print()
            print("AI moved %d to %d"%(seq[i][0], seq[i][1]))
    pegs_left = game.check_end()
    if pegs_left:
        playing = False
    elif not HUMAN_PLAYER:
        print("AI failed - game not finished")
        input("Press Enter to continue...")

game.print()
if HUMAN_PLAYER:
    print("You finished with %d pegs left!"%pegs_left)
    if pegs_left==1:
        print("YOU'RE A GENIUS")
    elif pegs_left==2:
        print("YOU'RE PURTY SMART")
    elif pegs_left==3:
        print("YOU'RE JUST PLAIN DUMB")
    elif pegs_left>=4:
        print("YOU'RE JUST PLAIN \"EG-NO-RA-MOOSE\"")
else:
    print("It finished with %d pegs left!"%pegs_left)
input("Press enter to finish...")

