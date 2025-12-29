# monte-carlo-f1-strategy

Small, focused Python project that uses Monte Carlo simulation to explore Formula 1 race strategies (pit stops, tyre choices, safety car effects). Useful for experimenting with strategy trade-offs and visualizing expected outcomes.

## Features
- Simple Monte Carlo engine to simulate race laps and pit stops
- Configurable tyre compounds, stint lengths, and safety car probability
- Outputs basic summary statistics (win/finish probabilities, average race time)

## Requirements
- Python 3.8+
- (Optional) Create a virtual environment and install dependencies if a `requirements.txt` is provided:
  ```
  python -m venv .venv
  source .venv/bin/activate   # or .venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

## Quick start
1. Clone the repo:
   ```
   git clone https://github.com/Arthavpatel/monte-carlo-f1-strategy.git
   cd monte-carlo-f1-strategy
   ```
2. Run the main simulation (adjust filename if different):
   ```
   python simulate.py --runs 10000 --strategy "1-stop"
   ```
3. Check the generated summary or plots in the output folder.

## Configuration & Usage
- Common flags:
  - `--runs`: number of Monte Carlo iterations
  - `--strategy`: strategy name or config file
  - `--seed`: RNG seed for reproducibility
- See `--help` on the main script for full options:
  ```
  python simulate.py --help
  ```

## Contributing
Contributions and improvements are welcome — open an issue or submit a PR. Keep changes small and add tests where applicable.
