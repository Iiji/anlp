
import matplotlib.pyplot as plt
import numpy as np


scores1 = {0: 17, 1: 33, 2: 29, 3: 11, 4: 8, 5: 2}
scores2 = {0: 23, 1: 37, 2: 19, 3: 12, 4: 7, 6: 2}
scores3 = {2: 13, 3: 9, 4: 21, 5: 14, 6: 18, 7: 8, 8: 7, 10: 10}


# Because the two sets of scores differ, we can combine and sort them to get a common scale
all_scores = range(0,11)

# We’ll align bars by using a known width and then shifting one set
bar_width = 0.3

aligned_freqs1 = [scores1.get(s,0) for s in all_scores]
aligned_freqs2 = [scores2.get(s,0) for s in all_scores]
aligned_freqs3 = [scores3.get(s,0) for s in all_scores]

# Create an index for each score
x = np.arange(len(all_scores))

fig, ax = plt.subplots(figsize=(10, 6))

ax.bar(x - bar_width, aligned_freqs1, width=bar_width, label='random guess', color='limegreen')
ax.bar(x, aligned_freqs2, width=bar_width, label='llava v1.5 7B', color='steelblue')
ax.bar(x + bar_width, aligned_freqs3, width=bar_width, label='ours*', color='orange')

# Add labels, title, and legend
ax.set_xlabel('Scores')
ax.set_ylabel('Frequency')
ax.set_title('Wordle scores of the last guess of two models')
ax.set_xticks(x)
ax.set_xticklabels(all_scores)
ax.legend()

plt.tight_layout()
plt.show()
plt.savefig('data/gameplay/wordle.png')