# Profit Analyzer

A modular, config-driven framework to compute portfolio Profit %, money-weighted and time-weighted returns,
compare against a benchmark (e.g., VTI), and generate plots. Designed to ingest Webull order CSVs out of the box.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="/mnt/d/Projects/profit_analyzer_package/src"
python -m profit_analyzer.main --config src/profit_analyzer/config/config.yaml
```

## Features
- Auto class discovery: add any class under `profit_analyzer/` and reference it by name in YAML.
- Parses Webull equity & options order exports.
- Computes Profit %, MWR (IRR) and TWR.
- Benchmark comparison via `yfinance` (default VTI).
- Matplotlib plots saved to `./plots`.
- Rotating file logs in `./logs`.
- Unit tests with pytest.



# 📊 Profit Analyzer

A modular, config-driven framework to analyze **Webull trade history**, calculate **profit percentages**, **money-weighted** and **time-weighted returns**, compare results with a **benchmark (e.g., VTI)**, and generate plots — all without editing code.

---

## 🚀 Features

- **Webull CSV parsing** — automatically reads equity and options order exports.
- **Automatic class discovery** — add new classes anywhere under `src/profit_analyzer/` and just list them in `config.yaml`.
- **Configuration-driven pipeline** — every module and parameter is loaded dynamically.
- **Logging** — rotating log files with timestamped INFO/DEBUG messages.
- **Metrics** — supports both Time-Weighted Return (TWR) and Money-Weighted Return (MWR / XIRR).
- **Visualization** — equity-curve and portfolio-vs-benchmark charts.
- **Unit tests** — full Pytest suite for reliability.

---

## 🧱 Project Structure
```
profit_analyzer/
├── data/ 
├── src/
│ └── profit_analyzer/
│ ├── config/
│ │ └── config.yaml
│ ├── core/
│ │ ├── file_loader.py
│ │ ├── webull_parser.py
│ │ ├── portfolio_builder.py
│ │ ├── profit_calculator.py
│ │ ├── price_provider.py
│ │ ├── benchmark_comparator.py
│ │ └── plotter.py
│ └── utils/
│ ├── logger.py
│ └── class_loader.py
├── tests/ 
├── requirements.txt
└── README.md
```
---

## ⚙️ Configuration (`config.yaml`)

```yaml
files:
  folder_path: "./data"
  include_patterns: ["Webull_Orders_Records*.csv"]

benchmark:
  ticker: "VTI"
  start_date: "2023-01-01"
  end_date: "2030-12-31"

returns:
  method: "time_weighted"     # or "money_weighted"

plot:
  output_dir: "./plots"

logging:
  level: "INFO"
  logfile: "./logs/profit_analyzer.log"
  max_bytes: 1048576
  backup_count: 5

modules:
  - class: FileLoader
    args:
      folder_path: "${files.folder_path}"
      include_patterns: "${files.include_patterns}"

  - class: WebullParser
    args: {}

  - class: PortfolioBuilder
    args: {}

  - class: ProfitCalculator
    args:
      method: "${returns.method}"

  - class: YFinancePriceProvider
    args: {}

  - class: BenchmarkComparator
    args:
      ticker: "${benchmark.ticker}"
      price_provider: "YFinancePriceProvider"

  - class: Plotter
    args:
      output_dir: "${plot.output_dir}"

```

## Installation

```bash
cd /mnt/d/Projects/profit_analyzer_package
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

```pgsql
[2025-10-25 19:09:49,404] INFO - Loaded 277 rows from CSVs
[2025-10-25 19:09:49,449] INFO - Parsed 52 filled trades across 14 symbols
[2025-10-25 19:09:49,483] INFO - Time-weighted return: 18.47%
Time-weighted return: 18.47%
```

generated files
```bash
./plots/equity_curve.png
./plots/portfolio_vs_benchmark.png
./logs/profit_analyzer.log
```

## How It Works
| Step | Module                    | Description                                                                                                |
| ---- | ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1    | **FileLoader**            | Reads all CSVs under `data/` matching your include patterns.                                               |
| 2    | **WebullParser**          | Cleans headers, parses timestamps, normalizes `Buy/Sell` sides, computes signed quantities and cash flows. |
| 3    | **PortfolioBuilder**      | Aggregates trades into positions and daily cash flows.                                                     |
| 4    | **ProfitCalculator**      | Computes TWR or MWR (XIRR).                                                                                |
| 5    | **YFinancePriceProvider** | Downloads historical prices for all symbols and benchmark from Yahoo Finance.                              |
| 6    | **BenchmarkComparator**   | Calculates cumulative benchmark returns for comparison.                                                    |
| 7    | **Plotter**               | Saves charts under `./plots/`.                                                                             |
| 8    | **Logger**                | Writes both console and rotating file logs.                                                                |


## Auto Class Discovery

class_loader.py automatically scans all sub-modules

```python
from profit_analyzer.utils.class_loader import discover_classes
classes = discover_classes("profit_analyzer")
```
Every class listed in config.yaml is instantiated with its args — no manual imports required.

## Running Tests

```bash
pytest -v
```
Covers file loading, parsing, calculations, benchmarks, and class discovery.

## Metrics Explained

| Metric                          | Meaning                                                    |
| ------------------------------- | ---------------------------------------------------------- |
| **TWR (Time-Weighted Return)**  | Measures performance independent of deposits/withdrawals.  |
| **MWR (Money-Weighted / XIRR)** | Accounts for timing and size of cash flows.                |
| **Equity Curve**                | Portfolio value over time (mark-to-market).                |
| **Benchmark Comparison**        | Overlay of portfolio vs. selected benchmark (default VTI). |


## Aditional info

- Switch between TWR and MWR:
```yaml
returns:
  method: "money_weighted"
```

- Change benchmark ticker, e.g.:
```yaml
benchmark:
  ticker: "QQQ"
```

- Add more Webull files to data/ — they’re auto-merged.

- Increase verbosity:
```yaml
logging:
  level: "DEBUG"
```

### Future Enhancements

- Multi-broker adapters (Fidelity, IBKR, Robinhood)
- Options Greeks and implied volatility analytics
- Portfolio allocation heatmaps
- Interactive Plotly dashboards

Author: Joseph Sankoorikal Johny
