# Sudoku Solver Performance Comparison

This repository contains Python implementations of two algorithms for solving Sudoku puzzles and includes a script to compare their performance using a large dataset. The primary goal is to demonstrate the effectiveness of incorporating deterministic deduction (a "Definitive Logic Chain") and intelligent cell selection (Minimum Remaining Values heuristic) into a backtracking search, compared to a simpler, traditional backtracking approach.

The project was inspired by running a performance race against a million Sudoku puzzles from a Kaggle dataset.

## Features

*   Implementation of a Traditional Backtracking Sudoku Solver.
*   Implementation of a Guess-augmented Definitive Logic Chain (GDLC) Sudoku Solver, incorporating constraint propagation and the Minimum Remaining Values (MRV) heuristic.
*   Script to read Sudoku puzzles from a CSV file (quizzes and solutions).
*   Ability to sample a percentage of puzzles from the dataset for testing.
*   Time race between the two solvers on the sampled puzzles.
*   Periodic and final reporting of performance statistics (average, min, max, standard deviation) and correctness.

## Algorithms

This project compares two distinct approaches to solving Sudoku puzzles. Both are based on backtracking but differ significantly in how they explore the search space.

### 1. Traditional Backtracking

This is a standard recursive backtracking algorithm. It works as follows:

1.  **Find Next Empty Cell:** Scan the grid (typically row by row, column by column) to find the very first empty cell (represented by 0).
2.  **Base Case:** If no empty cells are found, the puzzle is solved. Return the grid.
3.  **Try Digits:** For the found empty cell, attempt to place digits from 1 to 9, one by one.
4.  **Check Validity:** For each digit, check if placing it in the current cell is valid according to Sudoku rules (no conflicts in the row, column, or 3x3 box).
5.  **Recurse:** If a digit is valid, place it in the cell and recursively call the solver function for the updated grid.
6.  **Success:** If the recursive call returns a solved grid (not `None`), it means a solution was found down this path. Propagate the solved grid back up the call stack.
7.  **Backtrack:** If the recursive call returns `None` (meaning the chosen digit did not lead to a solution), undo the placement (reset the cell to 0) and try the next digit in the `Try Digits` step.
8.  **Failure:** If all digits from 1 to 9 have been tried for the current cell and none led to a solution, return `None`, signaling to the previous recursive call that this path is fruitless.

This method explores possibilities exhaustively but can be inefficient as it might make guesses early on without exhausting simple deterministic steps.

### 2. Guess-augmented Definitive Logic Chain (GDLC)

This algorithm, which I've termed GDLC, enhances the backtracking approach with constraint propagation techniques often used by human solvers. It prioritizes deterministic steps before resorting to guessing and uses a heuristic to make more informed guesses when necessary.

The process can be broken down into phases within the recursive calls:

1.  **Definitive Logic Chain (DLC) Phase:**
    *   Repeatedly iterate through the entire grid.
    *   For each empty cell, determine all *possible* valid digits it could contain based on the current state of the grid (check row, column, and box constraints).
    *   If a cell has *only one* possible valid digit, it's a *definitive* move. Fill this cell with that digit.
    *   Keep track of whether any cells were filled in a full pass over the grid.
    *   If any cells *were* filled, repeat this entire DLC phase. Filling one cell might create new definitive moves elsewhere. Continue until a full pass results in no new cells being filled deterministically.
    *   **Constraint Propagation:** If at any point during this phase an empty cell is found to have *zero* possible valid digits, it means the current state of the grid is impossible (a contradiction). This indicates a previous guess was incorrect. Immediately return `None` to trigger backtracking.

2.  **Check for Solution:** After the DLC phase completes (no more deterministic moves can be made), check if the grid is fully filled. If it is, the puzzle is solved. Return the grid.

3.  **Guessing (Bottleneck) Phase:**
    *   If the grid is not yet solved after the DLC phase, it means we've reached a "bottleneck" where no single deterministic move is possible. Guessing is required.
    *   **Cell Selection Heuristic (Minimum Remaining Values - MRV):** Instead of picking the next empty cell in a fixed order, scan all empty cells and find the one with the *fewest* possible valid digits (as determined during the DLC phase). This heuristic is chosen because:
        *   It reduces the branching factor in the search tree at this point.
        *   If a guess for this cell is wrong, a contradiction (an empty cell with zero possibilities, handled by the DLC phase on the next recursive call) is likely to be discovered faster, leading to earlier backtracking and pruning of the search space.
    *   Get the list of possible digits for the selected "best" cell.
    *   **Make a Posit (Guess) and Recurse:** Iterate through the possible digits for the chosen cell. For each digit:
        *   Place the digit in the cell (this is the "posit").
        *   Recursively call the `solve_sudoku_gdlc` function with the updated grid. This recursive call will *start again* with its own DLC phase based on this new guess.
    *   **Success:** If the recursive call returns a solved grid (not `None`), propagate this solution back up the call stack.
    *   **Backtrack:** If the recursive call returns `None`, the guess was incorrect. Undo the placement (reset the cell to 0) and try the next possible digit for the current bottleneck cell.

4.  **Exhausted Possibilities:** If all possible digits for the chosen bottleneck cell have been tried and none led to a solution, return `None`, signaling failure up the call stack and triggering backtracking at the previous guess level.

This GDLC method is expected to be more efficient than traditional backtracking because the DLC phase often solves a significant portion of the puzzle deterministically before any guessing occurs, and the MRV heuristic helps make more intelligent guesses when guessing is unavoidable.

## Performance Comparison

A time race was conducted using the full 1 million puzzles from the specified dataset to compare the performance of the two solver algorithms.

**Data Source:**

The puzzles used for the performance comparison are from the [Sudoku dataset on Kaggle by Bryan Park](https://www.kaggle.com/datasets/bryanpark/sudoku). This dataset contains 1 million Sudoku games and their corresponding solutions.

**Test Setup:**

*   **Dataset Size:** The comparison was run on the **entire dataset of 1,000,000 puzzles**.
*   **Hardware:** (You might want to add details about the CPU/RAM used here for better reproducibility, e.g., "Run on a [Your CPU Name] with [Your RAM Amount] RAM.")
*   **Code:** The Python script in this repository was used, with the `SAMPLE_PERCENTAGE` set to `1.0` to include all puzzles.

**Results:**

Here are the final statistics from running both solvers against all 1,000,000 puzzles:

| Metric                  | GDLC Solver     | Traditional Solver |
| :---------------------- | :-------------- | :----------------- |
| Total puzzles processed | 1,000,000       | 1,000,000          |
| Correctly Solved        | 1,000,000       | 1,000,000          |
| Failed to Solve         | 0               | 0                  |
| **Average time (sec)**  | **0.000468**    | 0.000889           |
| Min time (sec)          | 0.000156        | 0.000172           |
| Max time (sec)          | 0.032885        | 0.118753           |
| **Std Dev time (sec)**  | **0.000270**    | 0.001124           |

**Analysis:**

The results from the large-scale test clearly demonstrate the performance advantage of the GDLC solver compared to the Traditional Backtracking solver:

*   **Average Speed:** The GDLC solver is significantly faster on average, completing puzzles in approximately **half the time** (0.000468s) compared to the Traditional solver (0.000889s).
*   **Consistency:** The standard deviation of execution times for GDLC (0.000270s) is substantially lower than that for the Traditional solver (0.001124s). This indicates that the GDLC solver's performance is much more consistent and less affected by variations in puzzle structure or difficulty. The Traditional solver shows much higher variability in its solving times.
*   **Peak Performance:** The maximum time taken by the GDLC solver on any single puzzle (0.032885s) is also notably lower than the maximum time for the Traditional solver (0.118753s).
*   **Correctness:** Both algorithms successfully solved **100%** of the 1,000,000 puzzles tested, confirming their reliability.

The superior performance of the GDLC approach is attributed to its intelligent design: the Definitive Logic Chain (DLC) phase quickly resolves as many cells as possible using deterministic logic before resorting to guesses, and the Minimum Remaining Values (MRV) heuristic guides the guessing process by focusing on the most constrained cells, thus pruning the search space more effectively than a simple scan for the next empty cell.

## Visualization

To provide a clear visual comparison of the solver performance, the race script generates plots using Matplotlib.

### Average Solving Time

This bar chart compares the mean execution time of the two algorithms across the sampled puzzles.

![solving_time_distribution_box_plot](https://github.com/user-attachments/assets/63a89543-9200-401b-ab0f-22628f8e984d)


### Distribution of Solving Times

This box plot illustrates the distribution of execution times for both solvers. The box represents the interquartile range (25th to 75th percentile), the line inside is the median, and the whiskers extend to cover most of the remaining data. Points beyond the whiskers are typically considered outliers.

![average_solving_time_bar_chart](https://github.com/user-attachments/assets/790891e0-48bd-4149-a05a-efb418cfa1d5)


The visual differences in the plots, particularly the lower average bar and the tighter distribution (smaller box and whiskers) in the box plot for the GDLC solver, corroborate the statistical findings and emphasize its efficiency and consistency.


## How to Run

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory_name>

2.  **Download the dataset:**
    Download the `sudoku.csv` file from the Kaggle dataset link provided in the [Data Source](#data-source) section.

3.  **Place the data file:**
    Place the downloaded `sudoku.csv` file in the same directory as the Python script (`sudoku_solver_race.py`).

4.  **Run the script:**
    Execute the Python script from your terminal:
    ```bash
    python sudoku_solver_race.py
    ```

The script will read the puzzles, randomly sample a percentage (defaulting to 5% unless modified), run the solvers, and print cumulative statistics periodically, followed by the final summary statistics.

**Configuration:**

You can modify parameters directly in the `sudoku_solver_race.py` file:

*   `CSV_FILENAME`: Name of the CSV file (`"sudoku.csv"`).
*   `SAMPLE_PERCENTAGE`: The fraction of the total puzzles to sample (e.g., `0.05` for 5%, `1.0` for 100%). **Set this to `1.0` to replicate the 1M puzzle test results shown above.**
*   `STATS_REPORT_INTERVAL`: How often (in number of puzzles processed) cumulative statistics are printed during the race (e.g., `5000`).

## Data File Format (`sudoku.csv`)

The expected format of the CSV file is two columns with a header row:

```csv
quizzes,solutions
004300209005009001070060043006002087190007400050083000600000105003508690042910300,864371259325849761971265843436192587198657432257483916689734125713528694542916378
... (subsequent rows with quiz,solution pairs) ...
