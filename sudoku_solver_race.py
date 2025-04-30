import time
import csv
import random
import statistics
import os # To check if the file exists

# --- Helper Functions (Shared) ---

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

# print_grid function - kept for potential debugging but NOT used in the main race loop
def print_grid(grid):
    """Prints the Sudoku grid in a readable format, showing 0s for blanks."""
    if grid is None:
        print("No solution exists.")
        return

    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - ")

        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            print(str(grid[i][j]) + (" " if j < 8 else ""), end="")
        print() # Newline after each row
    print() # Extra newline after the grid

# Helper to convert the 81-char string from CSV to a 9x9 grid (list of lists of ints)
def string_to_grid(puzzle_string):
    """Converts an 81-character string of digits into a 9x9 list of lists (int)."""
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            # Convert character digit to integer
            row.append(int(puzzle_string[i * 9 + j]))
        grid.append(row)
    return grid

# Helper to convert a 9x9 grid (list of lists of ints) back to an 81-char string
def grid_to_string(grid):
    """Converts a 9x9 grid (list of lists of ints) to an 81-character string."""
    if grid is None:
        return None
    return ''.join(map(str, [cell for row in grid for cell in row]))


# --- GDLC (Guess-augmented Definitive Logic Chain) Algorithm ---

# Helper function for GDLC: find all possible valid digits for a given cell
def get_possible_digits_gdlc(grid, row, col):
    """Returns a list of numbers (1-9) that are valid options for grid[row][col]."""
    if grid[row][col] != 0:
        return [] # Cell is already filled

    possibilities = []
    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            possibilities.append(num)
    return possibilities

# Helper function for GDLC: find the empty cell with the minimum number of possibilities (MRV heuristic)
def find_best_cell_to_guess_gdlc(grid):
    """Finds the empty cell with the fewest valid possibilities for GDLC. Returns (row, col) or None."""
    best_cell = None
    min_possibilities = 10 # More than any cell can have

    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                possibilities_count = len(get_possible_digits_gdlc(grid, r, c))
                if possibilities_count == 0:
                    return (r, c) # Return this invalid cell to quickly prune the branch
                if possibilities_count < min_possibilities:
                    min_possibilities = possibilities_count
                    best_cell = (r, c)

    return best_cell # Returns None if no empty cells found

# Main GDLC solver function
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
        invalid_state = False
        for r in range(9):
            for c in range(9):
                if current_grid[r][c] == 0: # If the cell is empty
                    possibilities = get_possible_digits_gdlc(current_grid, r, c)

                    if len(possibilities) == 1:
                        current_grid[r][c] = possibilities[0]
                        filled_this_round = True
                    elif len(possibilities) == 0:
                        invalid_state = True
                        break
            if invalid_state:
                break

        if invalid_state:
            return None

        if not filled_this_round:
            break

    # --- Check if Solved After DLC ---
    is_solved = True
    for r in range(9):
        for c in range(9):
            if current_grid[r][c] == 0:
                is_solved = False
                break
        if not is_solved:
            break

    if is_solved:
        return current_grid

    # --- Guessing (Bottleneck) Phase ---
    best_cell = find_best_cell_to_guess_gdlc(current_grid)

    if best_cell is None: # Should only happen if solved or input invalid
         return None

    # Check possibilities again for the chosen cell as state might have changed slightly
    # Use the state *after* the DLC phase
    possibilities = get_possible_digits_gdlc(current_grid, best_cell[0], best_cell[1])
    if not possibilities: # If somehow no possibilities remain for the chosen cell
        return None

    row, col = best_cell

    for guess in possibilities:
        current_grid[row][col] = guess
        result = solve_sudoku_gdlc(current_grid) # Recursive call
        if result is not None:
            return result # Return the result from the successful recursive call
        current_grid[row][col] = 0 # Backtrack

    return None

# --- Traditional Backtracking Algorithm ---

# Helper function for Traditional: find the next empty cell by scanning
def find_next_empty_traditional(grid):
    """Finds the next empty cell (0) row by row, column by column. Returns (row, col) or None."""
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return (r, c)
    return None # No empty cells left

# Main Traditional Backtracking solver function
def solve_sudoku_traditional(grid):
    """
    Solves a Sudoku grid using a traditional recursive backtracking method.
    Returns the solved grid (as a new list) or None if no solution exists.
    """
    # Create a mutable copy of the grid to work with
    # Note: The recursive calls work on this same 'current_grid' object
    current_grid = [row[:] for row in grid]

    find = find_next_empty_traditional(current_grid)
    if not find:
        # Base case: No empty cells left, grid is solved
        return current_grid
    else:
        row, col = find

    for num in range(1, 10):
        # If placing num at (row, col) is valid
        if is_valid_move(current_grid, row, col, num):
            # Place the number
            current_grid[row][col] = num

            # Recursively try to solve the rest of the puzzle from this new state
            result = solve_sudoku_traditional(current_grid)

            # If the recursive call found a solution (returned a grid, not None)
            if result is not None:
                return result # Return the solved grid found by the recursive call

            # If the recursive call did NOT find a solution with 'num' in (row, col), backtrack
            current_grid[row][col] = 0

    # If tried all numbers 1-9 and none led to a solution from this cell
    return None # Signal failure up the call stack


# --- Time Race Setup and Execution ---

CSV_FILENAME = "sudoku.csv"
SAMPLE_PERCENTAGE = 1 # percentage of the total database
MIN_SAMPLE_SIZE = 1 # Ensure at least 1 puzzle is sampled if possible
STATS_REPORT_INTERVAL = 50000 # Report stats every this many puzzles

# --- Read Puzzles from CSV ---
puzzles = []
if not os.path.exists(CSV_FILENAME):
    print(f"Error: CSV file '{CSV_FILENAME}' not found in the current directory.")
    exit()

try:
    with open(CSV_FILENAME, 'r') as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header row
        for i, row in enumerate(reader):
            if len(row) >= 2:
                quizz_string = row[0]
                solution_string = row[1]
                if len(quizz_string) == 81 and len(solution_string) == 81:
                     # Basic check if it's a valid digit string before appending
                     if all(c.isdigit() for c in quizz_string) and all(c.isdigit() for c in solution_string):
                        puzzles.append((quizz_string, solution_string))
                     # else:
                     #     print(f"Warning: Skipping row {i+2} due to non-digit characters.")
                # else:
                #     print(f"Warning: Skipping row {i+2} due to incorrect length ({len(quizz_string)} or {len(solution_string)} != 81)")
            # else:
            #      print(f"Warning: Skipping row {i+2} due to incorrect number of columns ({len(row)} != 2)")

except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit()


if not puzzles:
    print(f"No valid puzzles found in '{CSV_FILENAME}'. Exiting.")
    exit()

total_puzzles = len(puzzles)
sample_size = max(MIN_SAMPLE_SIZE, int(total_puzzles * SAMPLE_PERCENTAGE))
sample_size = min(sample_size, total_puzzles) # Ensure sample size doesn't exceed total puzzles


print(f"Read {total_puzzles} puzzles from '{CSV_FILENAME}'.")
print(f"Sampling {sample_size} puzzles ({sample_size/total_puzzles:.1%} of total)...")

# Randomly sample indices
if sample_size == total_puzzles:
     sampled_indices = list(range(total_puzzles))
     random.shuffle(sampled_indices)
else:
    sampled_indices = random.sample(range(total_puzzles), sample_size)

sampled_puzzles_data = [puzzles[i] for i in sampled_indices]

# --- Run the Time Race ---
gdlc_times = []
traditional_times = []
gdlc_correct_count = 0
traditional_correct_count = 0
gdlc_failed_count = 0
traditional_failed_count = 0


print("\n--- Starting Time Race ---")
print(f"Running {sample_size} puzzles. Cumulative stats every {STATS_REPORT_INTERVAL} puzzles.")

for i, (puzzle_string, expected_solution_string) in enumerate(sampled_puzzles_data):
    original_grid = string_to_grid(puzzle_string)

    # Solve with GDLC
    grid_gdlc = [row[:] for row in original_grid] # Fresh copy
    start_time_gdlc = time.perf_counter()
    solved_grid_gdlc = solve_sudoku_gdlc(grid_gdlc)
    end_time_gdlc = time.perf_counter()
    elapsed_time_gdlc = end_time_gdlc - start_time_gdlc
    gdlc_times.append(elapsed_time_gdlc)

    # Validate GDLC result
    if solved_grid_gdlc is not None:
        solved_string_gdlc = grid_to_string(solved_grid_gdlc)
        if solved_string_gdlc == expected_solution_string:
             gdlc_correct_count += 1
        # else:
        #      print(f"\nWarning: GDLC produced INCORRECT solution for puzzle index {sampled_indices[i]+1}. Expected: {expected_solution_string[:10]}... Got: {solved_string_gdlc[:10]}...") # Print original index and snippet
    else:
         # If solver returned None, check if the puzzle was actually solvable (by checking if the traditional one solves it)
         # Or assume all puzzles in the list *are* solvable and count None as a failure to solve
         # For this race, we assume the provided puzzles are solvable, so None is a failure.
         gdlc_failed_count += 1


    # Solve with Traditional
    grid_traditional = [row[:] for row in original_grid] # Fresh copy
    start_time_traditional = time.perf_counter()
    solved_grid_traditional = solve_sudoku_traditional(grid_traditional)
    end_time_traditional = time.perf_counter()
    elapsed_time_traditional = end_time_traditional - start_time_traditional
    traditional_times.append(elapsed_time_traditional)

    # Validate Traditional result
    if solved_grid_traditional is not None:
         solved_string_traditional = grid_to_string(solved_grid_traditional)
         if solved_string_traditional == expected_solution_string:
              traditional_correct_count += 1
        #  else:
        #       print(f"\nWarning: Traditional produced INCORRECT solution for puzzle index {sampled_indices[i]+1}. Expected: {expected_solution_string[:10]}... Got: {solved_string_traditional[:10]}...") # Print original index and snippet
    else:
        traditional_failed_count += 1


    # --- Periodic Stats Reporting ---
    # Report stats every interval or on the last puzzle
    if (i + 1) % STATS_REPORT_INTERVAL == 0 or (i + 1) == sample_size:
        current_puzzles_processed = i + 1
        print(f"\n--- Cumulative Stats After {current_puzzles_processed} Puzzles ---")

        if gdlc_times: # Check if list is not empty
            print("GDLC Solver:")
            print(f"  Correctly Solved: {gdlc_correct_count}/{current_puzzles_processed}")
            print(f"  Failed to Solve:  {gdlc_failed_count}/{current_puzzles_processed}")
            # Ensure there are times recorded before calculating stats that require min/max/mean/stdev
            if current_puzzles_processed > 0:
                print(f"  Average time:     {statistics.mean(gdlc_times):.6f} seconds")
                print(f"  Min time:         {min(gdlc_times):.6f} seconds")
                print(f"  Max time:         {max(gdlc_times):.6f} seconds")
                if len(gdlc_times) > 1:
                    print(f"  Std Dev time:     {statistics.stdev(gdlc_times):.6f} seconds")
                else:
                    print("  Std Dev time:     N/A (sample size 1)")
            else:
                 print("  Time stats:       N/A (no puzzles processed)")

        if traditional_times: # Check if list is not empty
             print("\nTraditional Solver:")
             print(f"  Correctly Solved: {traditional_correct_count}/{current_puzzles_processed}")
             print(f"  Failed to Solve:  {traditional_failed_count}/{current_puzzles_processed}")
             if current_puzzles_processed > 0:
                print(f"  Average time:     {statistics.mean(traditional_times):.6f} seconds")
                print(f"  Min time:         {min(traditional_times):.6f} seconds")
                print(f"  Max time:         {max(traditional_times):.6f} seconds")
                if len(traditional_times) > 1:
                    print(f"  Std Dev time:     {statistics.stdev(traditional_times):.6f} seconds")
                else:
                    print("  Std Dev time:     N/A (sample size 1)")
             else:
                 print("  Time stats:       N/A (no puzzles processed)")
        print("--------------------------------------------------")


# --- Final Time Race Results ---
print("\n--- Final Time Race Results ---")

if gdlc_times:
    print("\nGDLC Solver Final Statistics:")
    print(f"  Total puzzles processed:  {len(gdlc_times)}")
    print(f"  Correctly Solved:       {gdlc_correct_count}/{len(gdlc_times)}")
    print(f"  Failed to Solve:        {gdlc_failed_count}/{len(gdlc_times)}")
    if len(gdlc_times) > 0:
        print(f"  Average time:           {statistics.mean(gdlc_times):.6f} seconds")
        print(f"  Min time:               {min(gdlc_times):.6f} seconds")
        print(f"  Max time:               {max(gdlc_times):.6f} seconds")
        if len(gdlc_times) > 1:
            print(f"  Std Dev time:           {statistics.stdev(gdlc_times):.6f} seconds")
        else:
            print("  Std Dev time:           N/A")


if traditional_times:
    print("\nTraditional Solver Final Statistics:")
    print(f"  Total puzzles processed:  {len(traditional_times)}")
    print(f"  Correctly Solved:       {traditional_correct_count}/{len(traditional_times)}")
    print(f"  Failed to Solve:        {traditional_failed_count}/{len(traditional_times)}")
    if len(traditional_times) > 0:
        print(f"  Average time:           {statistics.mean(traditional_times):.6f} seconds")
        print(f"  Min time:               {min(traditional_times):.6f} seconds")
        print(f"  Max time:               {max(traditional_times):.6f} seconds")
        if len(traditional_times) > 1:
            print(f"  Std Dev time:           {statistics.stdev(traditional_times):.6f} seconds")
        else:
            print("  Std Dev time:           N/A")


print("\n--- Race Complete ---")