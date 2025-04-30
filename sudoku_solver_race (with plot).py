import time
import csv
import random
import statistics
import os
import matplotlib.pyplot as plt # Import matplotlib

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
    # print() # Decided to remove this extra line break for slightly tighter output

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
    while True:
        filled_this_round = False
        invalid_state = False
        for r in range(9):
            for c in range(9):
                if current_grid[r][c] == 0:
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

    if best_cell is None:
         return None

    possibilities = get_possible_digits_gdlc(current_grid, best_cell[0], best_cell[1])
    if not possibilities:
        return None

    row, col = best_cell

    for guess in possibilities:
        current_grid[row][col] = guess
        result = solve_sudoku_gdlc(current_grid)
        if result is not None:
            return result
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
    current_grid = [row[:] for row in grid]

    find = find_next_empty_traditional(current_grid)
    if not find:
        return current_grid
    else:
        row, col = find

    for num in range(1, 10):
        if is_valid_move(current_grid, row, col, num):
            current_grid[row][col] = num

            result = solve_sudoku_traditional(current_grid) # Call recursively
            if result is not None: # Check if recursive call found a solution
                return result # Propagate the solution up

            current_grid[row][col] = 0 # Backtrack

    return None # No number worked for this cell


# --- Time Race Setup and Execution ---

CSV_FILENAME = "sudoku.csv"
SAMPLE_PERCENTAGE = 1.0 # Set to 1.0 for the 1 Million puzzle test
MIN_SAMPLE_SIZE = 1
STATS_REPORT_INTERVAL = 50000

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
                     if all(c.isdigit() for c in quizz_string) and all(c.isdigit() for c in solution_string):
                        puzzles.append((quizz_string, solution_string))

except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit()


if not puzzles:
    print(f"No valid puzzles found in '{CSV_FILENAME}'. Exiting.")
    exit()

total_puzzles = len(puzzles)
sample_size = max(MIN_SAMPLE_SIZE, int(total_puzzles * SAMPLE_PERCENTAGE))
sample_size = min(sample_size, total_puzzles)


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
    grid_gdlc = [row[:] for row in original_grid]
    start_time_gdlc = time.perf_counter()
    solved_grid_gdlc = solve_sudoku_gdlc(grid_gdlc)
    end_time_gdlc = time.perf_counter()
    elapsed_time_gdlc = end_time_gdlc - start_time_gdlc
    gdlc_times.append(elapsed_time_gdlc)

    if solved_grid_gdlc is not None:
        solved_string_gdlc = grid_to_string(solved_grid_gdlc)
        if solved_string_gdlc == expected_solution_string:
             gdlc_correct_count += 1
    else:
         gdlc_failed_count += 1


    # Solve with Traditional
    grid_traditional = [row[:] for row in original_grid]
    start_time_traditional = time.perf_counter()
    solved_grid_traditional = solve_sudoku_traditional(grid_traditional)
    end_time_traditional = time.perf_counter()
    elapsed_time_traditional = end_time_traditional - start_time_traditional
    traditional_times.append(elapsed_time_traditional)

    if solved_grid_traditional is not None:
         solved_string_traditional = grid_to_string(solved_grid_traditional)
         if solved_string_traditional == expected_solution_string:
              traditional_correct_count += 1
    else:
        traditional_failed_count += 1


    # --- Periodic Stats Reporting ---
    if (i + 1) % STATS_REPORT_INTERVAL == 0 or (i + 1) == sample_size:
        current_puzzles_processed = i + 1
        print(f"\n--- Cumulative Stats After {current_puzzles_processed} Puzzles ---")

        if gdlc_times:
            print("GDLC Solver:")
            print(f"  Correctly Solved: {gdlc_correct_count}/{current_puzzles_processed}")
            print(f"  Failed to Solve:  {gdlc_failed_count}/{current_puzzles_processed}")
            if current_puzzles_processed > 0:
                print(f"  Average time:     {statistics.mean(gdlc_times):.6f} seconds")
                print(f"  Min time:         {min(gdlc_times):.6f} seconds")
                print(f"  Max time:         {max(gdlc_times):.6f} seconds")
                if len(gdlc_times) > 1:
                    print(f"  Std Dev time:     {statistics.stdev(gdlc_times):.6f} seconds")
            else:
                 print("  Time stats:       N/A")

        if traditional_times:
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
                 print("  Time stats:       N/A")
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


# --- Matplotlib Visualization ---

def plot_average_times(gdlc_times, traditional_times):
    """Generates and saves a bar chart comparing average times."""
    if not gdlc_times or not traditional_times:
        print("Not enough data to generate average time plot.")
        return

    avg_gdlc = statistics.mean(gdlc_times)
    avg_traditional = statistics.mean(traditional_times)

    labels = ['GDLC', 'Traditional']
    averages = [avg_gdlc, avg_traditional]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, averages, color=['skyblue', 'lightcoral'])

    ax.set_ylabel('Average Execution Time (seconds)')
    ax.set_title('Average Sudoku Solving Time per Algorithm')
    ax.set_ylim(0, max(averages) * 1.2) # Set y-limit slightly above max for readability

    # Add text labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.6f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('average_solving_time_bar_chart.png')
    print("\nGenerated 'average_solving_time_bar_chart.png'")

def plot_time_distributions_box(gdlc_times, traditional_times):
    """Generates and saves a box plot comparing time distributions."""
    if not gdlc_times or not traditional_times:
         print("Not enough data to generate time distribution box plot.")
         return

    data = [gdlc_times, traditional_times]
    labels = ['GDLC', 'Traditional']

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create the box plot
    boxplot = ax.boxplot(data, patch_artist=True, medianprops=dict(color='black'))

    # Add colors
    colors = ['skyblue', 'lightcoral']
    for patch, color in zip(boxplot['boxes'], colors):
        patch.set_facecolor(color)

    # Add titles and labels
    ax.set_xticklabels(labels)
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Distribution of Sudoku Solving Times per Algorithm (Box Plot)')
    ax.grid(axis='y', linestyle='--') # Add a grid for better readability

    # Optional: Limit Y-axis to focus on the bulk of the data, clipping extreme outliers
    # This can make the main box/whiskers more visible if there are very large outliers.
    # You might need to adjust the upper limit based on your specific data distribution.
    # Example: ax.set_ylim(0, statistics.mean(traditional_times) * 5) # Or some other heuristic

    plt.tight_layout()
    plt.savefig('solving_time_distribution_box_plot.png')
    print("Generated 'solving_time_distribution_box_plot.png'")

# --- Call Plotting Functions After Race ---
if gdlc_times and traditional_times and sample_size > 0:
    print("\nGenerating plots...")
    plot_average_times(gdlc_times, traditional_times)
    plot_time_distributions_box(gdlc_times, traditional_times)
    print("Plot generation complete.")
else:
    print("\nSkipping plot generation: Not enough data from the race.")