import os
import matplotlib.pyplot as plt
import pandas as pd

class Plotter:
    def __init__(self, output_dir: str = "./plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_equity_curve(self, equity: pd.Series, label: str = "Portfolio"):
        plt.figure(figsize=(10,6))
        equity.plot()
        plt.title(f"{label} Equity Curve")
        plt.ylabel("Value")
        plt.xlabel("Date")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "equity_curve.png"))
        plt.close()

    def plot_vs_benchmark(self, portfolio_return_ts: pd.Series, benchmark: pd.DataFrame):
        plt.figure(figsize=(10,6))
        portfolio_return_ts.plot(label="Portfolio" )
        if benchmark is not None and not benchmark.empty:
            benchmark['return_pct'].plot(label="Benchmark" )
        plt.title("Portfolio vs Benchmark (Cum %)")
        plt.ylabel("Return (%)")
        plt.xlabel("Date")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "portfolio_vs_benchmark.png"))
        plt.close()
