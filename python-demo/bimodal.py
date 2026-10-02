# --- 1. Generate the bimodal dataset ---
import random

random.seed(123)

data = []

# First mode: mean=10, std=2
for _ in range(50):
    point = random.gauss(10, 2)
    point = round(point, 3)
    data.append(point)

# Second mode: mean=20, std=2
for _ in range(50):
    point = round(random.gauss(20, 2), 3)
    data.append(point)

print("Bimodal dataset:")
print(data)

# --- 2. Summarize the dataset ---
import pandas as pd

df = pd.DataFrame(data, columns=['value'])
print(df)

mean = df['value'].mean()
std_dev = df['value'].std()

print("\nSummary statistics:")
print("Mean:", round(mean, 3))
print("Standard Deviation:", round(std_dev, 3))

# --- 3. Plot the data as a histogram using pandas ---
import matplotlib.pyplot as plt

ax = df.plot.hist(y='value', bins=20)
ax.set_title('Histogram of Bimodal Dataset')
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
plt.show()
