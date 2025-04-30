import matplotlib.pyplot as plt
import numpy as np # Often useful with matplotlib

# --- Provided Results from Your 1 Million Puzzle Race ---
gdlc_avg_time = 0.000375
traditional_avg_time = 0.000707

# Note: Min, Max, and Std Dev times are provided but not used for a simple average bar chart.
# If you wanted to visualize standard deviation, you could add error bars to the bar chart,
# but generating a Box Plot requires the original data list, not just summary statistics.
# gdlc_min_time = 0.000154
# gdlc_max_time = 0.022399
# gdlc_std_dev = 0.000120
#
# traditional_min_time = 0.000195
# traditional_max_time = 0.058172
# traditional_std_dev = 0.000768


# --- Generate the Bar Chart ---

labels = ['GDLC', 'Traditional']
averages = [gdlc_avg_time, traditional_avg_time]

fig, ax = plt.subplots(figsize=(8, 6)) # Create a figure and an axes.

bars = ax.bar(labels, averages, color=['skyblue', 'lightcoral'])

# Add titles and labels
ax.set_ylabel('Average Execution Time (seconds)')
ax.set_title('Average Sudoku Solving Time per Algorithm (1 Million Puzzles)')
# Set y-limit slightly above max for readability
ax.set_ylim(0, max(averages) * 1.2)

# Add text labels on top of bars showing the exact value
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.6f}', ha='center', va='bottom')

# Add a slight margin at the top
plt.subplots_adjust(top=0.85)

plt.tight_layout() # Adjust layout to prevent labels overlapping
plt.savefig('average_solving_time_bar_chart.png') # Save the plot as a PNG file
print("Generated 'average_solving_time_bar_chart.png'")

# --- Explanation regarding Box Plot ---
print("\nNote: A Box Plot visualizing the distribution (median, quartiles, outliers)")
print("cannot be generated from only the average, min, max, and standard deviation.")
print("It requires access to the full list of individual solving times.")
print("The code above generates only the bar chart of averages.")

# Uncomment the line below to display the plot immediately after generating it
# plt.show()