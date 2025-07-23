import lasio
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl  # Needed for Excel export

# Load LAS file
las = lasio.read("data/sample.las")
df = las.df()

# Choose logs to work with
logs = ["GR", "RHOB", "NPHI"]
df = df[logs].dropna()

# Plot logs
fig, axes = plt.subplots(ncols=len(logs), sharey=True, figsize=(9, 6))
for ax, log in zip(axes, logs):
    ax.plot(df[log], df.index)
    ax.set_xlim(df[log].quantile(0.01), df[log].quantile(0.99))
    ax.set_xlabel(log)

axes[0].set_ylabel("Depth")
axes[0].fill_betweenx(df.index, df["GR"], df["GR"].max(), where=df["GR"] > 80, color="grey", alpha=0.3)
axes[0].set_title("Shale Zones (GR > 80)")
axes[0].invert_yaxis()
fig.tight_layout()
plt.show()

# Crossplot RHOB vs NPHI
plt.figure(figsize=(6, 5))
plt.scatter(df["RHOB"], df["NPHI"], c=df.index, cmap="viridis", s=4)
plt.xlabel("RHOB")
plt.ylabel("NPHI")
plt.title("Crossplot: RHOB vs NPHI")
plt.gca().invert_yaxis()
plt.colorbar(label="Depth")
plt.tight_layout()
plt.show()

# Pay zone detection logic
cut_gr = 60
cut_nphi = 0.2
cond = (df["GR"] < cut_gr) & (df["NPHI"] > cut_nphi)
df["Hydrocarbon"] = cond.astype(int)

# Group zones by depth continuity
df["zone_id"] = (df["Hydrocarbon"].diff(1) == 1).cumsum()
zones = df[df["Hydrocarbon"] == 1].groupby("zone_id").agg({
    "Hydrocarbon": "sum",
    lambda x: x.index.min(): "first",
    lambda x: x.index.max(): "last"
})
zones.columns = ["Count", "Top Depth", "Bottom Depth"]
zones["Thickness"] = zones["Bottom Depth"] - zones["Top Depth"]

# Export results
zones.to_excel("results/zones.xlsx")
df.to_excel("results/cleaned_logs.xlsx")

print("✔️ Export complete: cleaned logs & hydrocarbon zones saved to 'results/' folder.")
