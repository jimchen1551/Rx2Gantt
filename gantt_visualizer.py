import config
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

class GanttChartVisualizer:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def plot(self, output_path):
        """Generates and saves a Gantt chart from the dataframe."""
        # Sort data by start time
        df = self.dataframe.sort_values(by="開立時間")
        total_duration = (df["停止時間"].max() - df["開立時間"].min()).days

        # Create a unique color for each drug
        drugs = df["學名"].unique()
        color_map = {drug: plt.cm.get_cmap(config.CHART_COLOR_SCHEME)(i / len(drugs)) for i, drug in enumerate(drugs)}

        # Initialize the plot
        fig, ax = plt.subplots(figsize=(total_duration * 2, len(df) * 0.2))

        # Plot each drug's duration
        for _, row in df.iterrows():
            duration = row["停止時間"] - row["開立時間"]
            ax.barh(
                row["學名"], duration, left=row["開立時間"],
                color=color_map[row["學名"]], edgecolor="black"
            )

            # Add text annotations
            annotation = f"{row['劑量']} / {row['頻次']} / {row['途徑']}"
            ax.text(
                row["開立時間"] + duration / 2, row["學名"], annotation,
                ha="center", va="center", fontsize=10, color="black",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black")
            )

        # Format x-axis
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")

        # Define grid lines and labels
        min_time = df["開立時間"].min()
        max_time = df["停止時間"].max()

        # Create major and minor ticks
        time_ticks = pd.date_range(min_time.floor('D'), max_time.ceil('D'), freq='6h')
        major_ticks = pd.date_range(min_time.floor('D'), max_time.ceil('D'), freq='1D')

        ax.set_xticks(time_ticks, minor=True)
        ax.set_xticks(major_ticks, minor=False)

        # Format major ticks with day and date
        labels = [f"{tick.strftime('%Y-%m-%d')}\n{tick.strftime('%a')}" for tick in major_ticks]
        ax.set_xticklabels(labels, fontsize=10)

        # Format minor ticks
        ax.xaxis.set_minor_formatter(plt.NullFormatter())

        # Add grid lines
        ax.xaxis.grid(True, which="major", linestyle="--", linewidth=1.5, color="black")
        ax.xaxis.grid(True, which="minor", linestyle="--", linewidth=0.5, color="gray")

        # Invert y-axis to show the first drug at the top
        ax.invert_yaxis()
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        # Adjust layout and save the chart
        plt.tight_layout()
        plt.savefig(output_path)
        print(f"Gantt chart saved to {output_path}.")
