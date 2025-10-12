import random
import time

# --- Constants ---
RED = 'red'
BLUE = 'blue'
RED_START = -1
BLUE_START = -1
MAIN_TRACK_SIZE = 40
HOME_SIZE = 5
EXITED = 50

# --- Game State ---
class Player:
    def __init__(self, color):
        self.color = color
        self.pieces = [RED_START if color == RED else BLUE_START] * 4  # 4 pieces each
        self.name = "Denmark" if color == RED else "Sweden"
        self.symbol = 'R' if color == RED else 'B'

    def is_winner(self):
        return all(pos == EXITED for pos in self.pieces)

    def get_valid_moves(self, steps):
        valid_moves = []
        for i, pos in enumerate(self.pieces):
            if pos == EXITED:
                continue
            new_pos = self.calculate_new_position(pos, steps)
            if new_pos is not None:
                valid_moves.append(i)
        return valid_moves

    def calculate_new_position(self, current_pos, steps):
        if current_pos == RED_START and self.color == RED:
            return 0  # Enter at T0
        elif current_pos == BLUE_START and self.color == BLUE:
            return 20  # Enter at T20
        elif current_pos < 40:  # On main track
            if self.color == RED:
                new_pos = current_pos + steps
                if new_pos >= 40:
                    return 40 + (new_pos - 40)  # Enter red home
                else:
                    return new_pos
            else:  # Blue
                # Map current position to logical 0-39 (starting from T20)
                logical_pos = (current_pos - 20) % 40
                new_logical = logical_pos + steps
                if new_logical >= 40:
                    return 45 + (new_logical - 40)  # Enter blue home
                else:
                    return (new_logical + 20) % 40  # Map back to T0-T39
        elif current_pos < 45 and self.color == RED:  # In red home
            new_pos = current_pos + steps
            if new_pos >= 45:
                return EXITED
            else:
                return new_pos
        elif current_pos < 50 and self.color == BLUE:  # In blue home
            new_pos = current_pos + steps
            if new_pos >= 50:
                return EXITED
            else:
                return new_pos
        else:
            return EXITED  # Already exited

    def __str__(self):
        return f"{self.name} ({self.color.upper()})"

class Game:
    def __init__(self):
        self.red_player = Player(RED)
        self.blue_player = Player(BLUE)
        self.current_player = self.red_player  # Human starts
        self.main_track = [None] * MAIN_TRACK_SIZE  # None = empty, or store piece ID
        self.red_home = [None] * HOME_SIZE
        self.blue_home = [None] * HOME_SIZE
        self.turn_count = 0

    def roll_die(self):
        return random.randint(1, 6)

    def get_piece_at_position(self, pos):
        if pos < 0:
            return None
        elif pos < 40:
            return self.main_track[pos]
        elif pos < 45:
            return self.red_home[pos - 40]
        elif pos < 50:
            return self.blue_home[pos - 45]
        else:
            return None

    def set_piece_at_position(self, pos, piece_id):
        if pos < 0:
            return
        elif pos < 40:
            self.main_track[pos] = piece_id
        elif pos < 45:
            self.red_home[pos - 40] = piece_id
        elif pos < 50:
            self.blue_home[pos - 45] = piece_id

    def clear_position(self, pos):
        if pos < 0:
            return
        elif pos < 40:
            self.main_track[pos] = None
        elif pos < 45:
            self.red_home[pos - 40] = None
        elif pos < 50:
            self.blue_home[pos - 45] = None

    def move_piece(self, player, piece_idx, steps):
        current_pos = player.pieces[piece_idx]
        new_pos = player.calculate_new_position(current_pos, steps)

        if new_pos is None:
            return False

        collision_occurred = False
        collision_target = None

        # Handle collision only on main track
        if 0 <= new_pos < 40:
            occupant = self.get_piece_at_position(new_pos)
            if occupant is not None:
                # Collision! Send opponent piece back to start
                if occupant.startswith('R') and player.color == BLUE:
                    self.return_piece_to_start('R', occupant[1])
                    collision_occurred = True
                    collision_target = f"Red piece {occupant[1]}"
                elif occupant.startswith('B') and player.color == RED:
                    self.return_piece_to_start('B', occupant[1])
                    collision_occurred = True
                    collision_target = f"Blue piece {occupant[1]}"

        # Clear old position
        if 0 <= current_pos < 40:
            self.clear_position(current_pos)
        elif 40 <= current_pos < 45:
            self.clear_position(current_pos)
        elif 45 <= current_pos < 50:
            self.clear_position(current_pos)

        # Update player's piece position
        player.pieces[piece_idx] = new_pos

        # Set new position
        if new_pos < 40:
            self.set_piece_at_position(new_pos, f"{player.symbol}{piece_idx}")
        elif 40 <= new_pos < 45:
            self.set_piece_at_position(new_pos, f"{player.symbol}{piece_idx}")
        elif 45 <= new_pos < 50:
            self.set_piece_at_position(new_pos, f"{player.symbol}{piece_idx}")

        # Report collision
        if collision_occurred:
            print(f"💥 {player.name} knocks back {collision_target} to start! 💥")

        return True

    def return_piece_to_start(self, color, piece_idx_str):
        piece_idx = int(piece_idx_str)
        if color == 'R':
            self.red_player.pieces[piece_idx] = RED_START
            self.clear_position(self.get_piece_position(f"R{piece_idx}"))
        else:
            self.blue_player.pieces[piece_idx] = BLUE_START
            self.clear_position(self.get_piece_position(f"B{piece_idx}"))

    def get_piece_position(self, piece_id):
        # Helper to find where a piece is currently located
        for i, pos in enumerate(self.red_player.pieces):
            if f"R{i}" == piece_id:
                return pos
        for i, pos in enumerate(self.blue_player.pieces):
            if f"B{i}" == piece_id:
                return pos
        return None

    def display_board(self):
        print("\n" + "="*60)
        print("           🇩🇰 DENMARK (RED) vs 🇸🇪 SWEDEN (BLUE)           ")
        print("="*60)
        print(f"Turn: {self.turn_count} | Current Player: {self.current_player}")
        print(f"Red Pieces: {[pos if pos != EXITED else '✅' for pos in self.red_player.pieces]}")
        print(f"Blue Pieces: {[pos if pos != EXITED else '✅' for pos in self.blue_player.pieces]}")
        print()

        # Display main track (T0 to T39)
        print("Main Track (T0 to T39):")
        track_str = ""
        for i in range(MAIN_TRACK_SIZE):
            occupant = self.main_track[i]
            if occupant is None:
                track_str += f"[{i:2d}] "
            else:
                track_str += f"[{occupant}] "
            if (i + 1) % 10 == 0:
                track_str += "\n"
        print(track_str)

        # Display home zones
        print("\nRed Home (40-44): " + " ".join([f"[{self.red_home[i] or ' '}] " for i in range(HOME_SIZE)]))
        print("Blue Home (45-49): " + " ".join([f"[{self.blue_home[i] or ' '}] " for i in range(HOME_SIZE)]))
        print("="*60)

    def get_human_move(self, steps):
        valid_moves = self.current_player.get_valid_moves(steps)
        if not valid_moves:
            print("No valid moves. Skipping turn.")
            return None

        print(f"\nYou rolled: {steps}")
        print(f"Valid pieces to move: {valid_moves}")
        while True:
            try:
                choice = int(input("Choose piece to move (0-3): "))
                if choice in valid_moves:
                    return choice
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")

    def get_computer_move(self, steps):
        valid_moves = self.current_player.get_valid_moves(steps)
        if not valid_moves:
            print("Computer has no valid moves. Skipping turn.")
            return None

        best_score = -1
        best_move = valid_moves[0]

        for piece_idx in valid_moves:
            score = self.evaluate_move(self.current_player, piece_idx, steps)
            if score > best_score:
                best_score = score
                best_move = piece_idx

        print(f"🤖 Computer chooses piece {best_move} (score: {best_score})")
        return best_move

    def evaluate_move(self, player, piece_idx, steps):
        current_pos = player.pieces[piece_idx]
        new_pos = player.calculate_new_position(current_pos, steps)

        score = 0

        # 1. WINNING MOVE: If this move gets the piece to EXITED (goal)
        if new_pos == EXITED:
            # Bonus: if this is the 4th piece, it's a win!
            if player.pieces.count(EXITED) == 3:  # 3 already exited, this is 4th
                score += 30  # Huge bonus for winning
            else:
                score += 20  # Still good, but not game-ending
            return score  # Winning moves are highest priority

        # 2. AGGRESSION: Does this move knock back opponent?
        if 0 <= new_pos < 40:
            occupant = self.get_piece_at_position(new_pos)
            if occupant is not None:
                if (occupant.startswith('R') and player.color == BLUE) or \
                   (occupant.startswith('B') and player.color == RED):
                    score += 20  # Big bonus for knocking back
                    return score  # Knocking back is almost as good as winning

        # 3. STRIKING DISTANCE: Can this move put us within 6 steps of an opponent piece?
        if 0 <= new_pos < 40:  # Only on main track
            opponent_pieces = []
            if player.color == RED:
                opponent_pieces = [(i, pos) for i, pos in enumerate(self.blue_player.pieces) if 0 <= pos < 40]
            else:
                opponent_pieces = [(i, pos) for i, pos in enumerate(self.red_player.pieces) if 0 <= pos < 40]

            for opp_idx, opp_pos in opponent_pieces:
                # Calculate distance from new_pos to opp_pos (considering Blue's wrap-around)
                if player.color == RED:
                    distance = abs(new_pos - opp_pos)
                else:  # Blue
                    # Blue’s path: 20→39→0→19
                    # So we map both positions to logical 0-39
                    new_logical = (new_pos - 20) % 40
                    opp_logical = (opp_pos - 20) % 40
                    distance = min(
                        abs(new_logical - opp_logical),
                        40 - abs(new_logical - opp_logical)
                    )
                if distance <= 6:  # Within striking distance
                    score += 15  # Good bonus for positioning
                    break  # One is enough — don’t stack

        # 4. PROGRESSION: How far is the piece from exiting?
        if new_pos < 40:  # Still on main track
            if player.color == RED:
                distance_to_home = 40 - new_pos
            else:  # Blue
                logical_pos = (new_pos - 20) % 40
                distance_to_home = 40 - logical_pos
            score += max(0, 10 - distance_to_home)  # Bonus for getting closer
        elif 40 <= new_pos < 45 and player.color == RED:
            score += 5 + (new_pos - 40)  # Bonus for advancing in home
        elif 45 <= new_pos < 50 and player.color == BLUE:
            score += 5 + (new_pos - 45)  # Bonus for advancing in home

        return score

    def play_turn(self):
        self.turn_count += 1
        steps = self.roll_die()
        print(f"\n{self.current_player} rolls: {steps}")

        if self.current_player == self.red_player:
            piece_idx = self.get_human_move(steps)
        else:
            piece_idx = self.get_computer_move(steps)

        if piece_idx is not None:
            success = self.move_piece(self.current_player, piece_idx, steps)
            if success:
                print(f"{self.current_player} moved piece {piece_idx}.")

        # Check win condition
        if self.red_player.is_winner():
            print("\n🎉🎉🎉 DENMARK WINS! 🇩🇰🎉🎉🎉")
            return True
        elif self.blue_player.is_winner():
            print("\n🎉🎉🎉 SWEDEN WINS! 🇸🇪🎉🎉🎉")
            return True

        # Switch player
        self.current_player = self.blue_player if self.current_player == self.red_player else self.red_player
        return False

    def run(self):
        print("Welcome to Fia / Mensch ärgere Dich nicht!")
        print("Red (Denmark) starts. Blue (Sweden) is computer.")
        print("No special rules: any roll moves a piece onto board. Overshooting home is fine.")
        print("Collision on main track sends opponent back to start.")
        print("First to get all 4 pieces off the board wins.\n")

        while True:
            self.display_board()
            if self.play_turn():
                break
            time.sleep(1)  # Pause for readability

# --- Main ---
if __name__ == "__main__":
    game = Game()
    game.run()
