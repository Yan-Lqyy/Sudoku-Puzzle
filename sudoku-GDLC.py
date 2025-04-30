import math

# Helper function to check if placing 'num' at grid[row][col] is valid
def is_valid_move(grid, row, col, num):
    """Checks if placing 'num' at grid[row][col] is valid according to Sudoku rules."""
    # Check row
    if num in grid[row]:
        return False

    # Check column
    if num in [grid[i][col] for i in range(9)]:
        return False

    # Check 3x3 box
    start_row = 3 * (row // 3)
    start_col = 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False

    return True

# Helper function to find all possible valid digits for a given cell
def get_possible_digits(grid, row, col):
    """Returns a list of numbers (1-9) that are valid options for grid[row][col]."""
    if grid[row][col] != 0:
        return [] # Cell is already filled

    possibilities = []
    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            possibilities.append(num)
    return possibilities

# Helper function to find the empty cell with the minimum number of possibilities (MRV heuristic)
def find_best_cell_to_guess(grid):
    """Finds the empty cell with the fewest valid possibilities. Returns (row, col) or None."""
    best_cell = None
    min_possibilities = 10 # More than any cell can have

    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                possibilities_count = len(get_possible_digits(grid, r, c))
                if possibilities_count < min_possibilities:
                    min_possibilities = possibilities_count
                    best_cell = (r, c)

    return best_cell # Returns None if no empty cells found

# Main solver function implementing the GDLC method
def solve_sudoku_gdlc(grid):
    """
    Solves a Sudoku grid using the GDLC (Guess-augmented Definitive Logic Chain) method.
    Returns the solved grid (as a new list) or None if no solution exists.
    """
    # Create a mutable copy of the grid to work with
    current_grid = [row[:] for row in grid]

    # --- Definitive Logic Chain (DLC) Phase ---
    # Repeatedly fill cells that have only one possible valid digit
    while True:
        filled_this_round = False
        for r in range(9):
            for c in range(9):
                if current_grid[r][c] == 0: # If the cell is empty
                    possibilities = get_possible_digits(current_grid, r, c)

                    if len(possibilities) == 1:
                        # Found a cell with only one possibility - this is a definitive move (part of DLC)
                        current_grid[r][c] = possibilities[0]
                        filled_this_round = True
                    elif len(possibilities) == 0:
                        # If a cell has 0 possibilities at this stage, the current grid state is invalid.
                        # This can happen if a previous guess was wrong.
                        return None # Indicate failure up the call stack

        # If we didn't fill any cells in a full pass, the DLC phase is complete.
        # If we did fill cells, repeat the DLC phase as new fills might create new single possibilities.
        if not filled_this_round:
            break

    # --- Check if Solved After DLC ---
    # After the DLC phase, see if the puzzle is complete.
    is_solved = True
    for r in range(9):
        for c in range(9):
            if current_grid[r][c] == 0:
                is_solved = False
                break
        if not is_solved:
            break

    if is_solved:
        # Grid is full and (by design of DLC) must be valid if we didn't return None
        return current_grid

    # --- Guessing (Bottleneck) Phase ---
    # If not solved, we've hit a bottleneck. Need to make a guess.
    # Use the MRV heuristic to pick the best cell to guess on.
    best_cell = find_best_cell_to_guess(current_grid)

    # This case should theoretically be covered by the is_solved check,
    # but as a safeguard:
    if best_cell is None:
         # No empty cells found, but it wasn't marked solved? Should not happen in valid puzzles.
         # For robustness, return None or the current grid (which is likely invalid here)
         # Let's return None as it indicates something unexpected or an invalid starting puzzle.
         return None # Or perhaps return current_grid if you trust the DLC phase implicitly solved it

    row, col = best_cell
    possibilities = get_possible_digits(current_grid, row, col) # Get the possibilities for the chosen cell

    # Iterate through each possible digit for the chosen cell
    for guess in possibilities:
        # --- Make a posit (Guess) ---
        current_grid[row][col] = guess

        # --- Continue with a guess-based DLC (Recursive Call) ---
        # Recursively try to solve the grid starting with this guess.
        # The next call will begin with *its own* DLC phase based on this guess.
        result = solve_sudoku_gdlc(current_grid)

        # If the recursive call returned a solution (not None), propagate it up.
        if result is not None:
            return result # Solution found down this path!

        # --- Backtrack ---
        # If the recursive call did NOT find a solution with this guess,
        # undo the guess and try the next possibility for the current cell.
        current_grid[row][col] = 0 # Reset the cell to empty

    # --- Exhausted Possibilities ---
    # If the loop finishes, it means none of the possibilities for the chosen cell
    # led to a solution. The current path is invalid.
    return None # Indicate failure up the call stack

# Helper function to print the Sudoku grid nicely
def print_grid(grid):
    """Prints the Sudoku grid in a readable format."""
    if grid is None:
        print("No solution exists.")
        return

    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - ") # Separator for boxes
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(" | ", end="") # Separator for boxes
            if j == 8:
                print(grid[i][j])
            else:
                print(str(grid[i][j]) + " ", end="")
    print()

# --- Example Usage ---
# A standard medium difficulty Sudoku puzzle
example_grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

print("Original Puzzle:")
print_grid(example_grid)

print("Solving...")
solved_grid = solve_sudoku_gdlc(example_grid)

print("Solved Puzzle (GDLC Method):")
print_grid(solved_grid)

# Another example - a harder one
hard_grid = [
    [0, 0, 0, 6, 0, 0, 4, 0, 0],
    [7, 0, 0, 0, 0, 3, 6, 0, 0],
    [0, 0, 0, 0, 9, 1, 0, 8, 0],
    [0, 0, 0, 0, 0, 5, 0, 7, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [9, 7, 0, 3, 0, 0, 0, 0, 0],
    [0, 8, 0, 4, 1, 0, 0, 0, 0],
    [0, 0, 3, 8, 0, 0, 0, 0, 6],
    [0, 0, 6, 0, 0, 2, 0, 0, 0]
]

print("Original Hard Puzzle:")
print_grid(hard_grid)

print("Solving...")
solved_hard_grid = solve_sudoku_gdlc(hard_grid)

print("Solved Hard Puzzle (GDLC Method):")
print_grid(solved_hard_grid)

# Example of an unsolvable grid (intentionally created contradiction)
unsolvable_grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
    # Add a deliberate contradiction, e.g., put a 5 in row 0, col 1 (already has 3, 5 is in col 0)
    # Let's make it simpler and directly modify the standard grid to be unsolvable after one step
    # Put a 5 in cell (0,1) which is already 3, and 5 is in (0,0)
]

unsolvable_grid_example = [
    [5, 5, 0, 0, 7, 0, 0, 0, 0], # Row 0 has two 5s - invalid
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

print("Original Unsolvable Puzzle Example:")
print_grid(unsolvable_grid_example)

print("Solving...")
solved_unsolvable_grid = solve_sudoku_gdlc(unsolvable_grid_example)

print("Solved Unsolvable Puzzle (GDLC Method):")
print_grid(solved_unsolvable_grid) # This should print "No solution exists."