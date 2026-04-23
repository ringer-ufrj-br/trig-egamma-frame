[![maestro](https://github.com/lps-ufrj-br/maestro-lightning/actions/workflows/flow.yml/badge.svg)](https://github.com/lps-ufrj-br/maestro-lighning/actions/workflows/flow.yml)
[![CI](https://github.com/ringer-ufrj-br/trig-egamma-frame/actions/workflows/ci.yml/badge.svg)](https://github.com/ringer-ufrj-br/trig-egamma-frame/actions/workflows/ci.yml)
# ⚡ trig-egamma-frame

> [!IMPORTANT]
> This software is the property of the **Federal University of Rio de Janeiro (UFRJ)**, developed in collaboration with **CERN** and the **Signal Processing Laboratory (LPS)**.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Framework: ROOT](https://img.shields.io/badge/ROOT-6.xx-orange.svg)](https://root.cern/)


A high-performance framework for **ATLAS Trigger Egamma emulation** and data processing. Designed for both Legacy (Run 2) and modern Run 3 data, this framework provides a modular and efficient environment to simulate trigger chains, optimize selectors (like Ringer), and dump analysis-ready data. 🚀

---

## 🌟 Key Features

- **🚀 Dual-Era Emulation**: Full support for legacy Run 2 (v1) and modern Run 3 (v2) trigger steps.
- **🧠 ML-Ready**: Built-in support for the **Ringer Selector** using TensorFlow/Keras and ONNX.
- **🏗️ Modular Architecture**: Leverages `Algorithm`, `StoreGate`, and `EDM` patterns for clean, extensible code.
- **📊 Fast Data Dumping**: Integrated `ElectronDumper` utilizing ROOT's `RDataFrame` for high-speed I/O.
- **🐳 Container Optimized**: Perfect for execution within Singularity/Apptainer environments.

---

## 🛠️ Installation

### 1. Requirements 📋
* **Python 3.8+**
* **CERN ROOT** (with PyROOT enabled)
* **TensorFlow** (optional, for Ringer emulation)

### 2. Local Setup 💻
The easiest way to install and manage the environment is using the provided `conda` configuration:

```bash
# Clone the repository
git clone https://github.com/ringer-ufrj-br/trig-egamma-frame.git
cd trig-egamma-frame

# Install dependencies and setup environment
make setup

# Activate the conda environment
source activate.sh
```

### 3. Using Singularity 🐳
For cluster environments (like CERN LXPLUS), it is recommended to use the containerized version:

```bash
# Download the image (using Makefile)
make pull

# Run the container with necessary volume binds
singularity run --bind /mnt/shared:/mnt/shared root_image.sif
```

---

## 📊 Dataframe Schemes

The framework handles different data eras through specific schemas:

| Version | Schema | Data Years | Description |
| :--- | :--- | :--- | :--- |
| **v1** | `DataframeSchemma.Run2` | 2017, 2018 | Legacy Run 2 data formats. |
| **v2** | `DataframeSchemma.Run3` | Run 3+ | Modern Run 3 data with updated EDM. |

---

## 🚀 Usage Example: Data Dumping

To perform a trigger emulation and dump the results into a ROOT file, you can utilize the `ElectronLoop` and `ElectronDumper`:

```python
from trig_egamma_frame import ElectronLoop, DataframeSchemma
from trig_egamma_frame.algorithms.dumper import ElectronDumper_v2 as ElectronDumper
from trig_egamma_frame.kernel import ToolSvc

# 1. Setup the Event Loop
# Use DataframeSchemma.Run2 for v1 (2017/18) or Run3 for v2 (Run 3)
loop = ElectronLoop(
    "MyAnalysis",
    inputFile  = "path/to/my/input.root",
    treePath   = "*/HLT/Physval/Egamma/probes",
    dataframe  = DataframeSchemma.Run2, # v1 data
    outputFile = "output.root"
)

# 2. Configure the Dumper
et_bins  = [3., 7., 10., 15., 20., 30., 40., 50., 1000.]
eta_bins = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]
dumper = ElectronDumper("dumper_output", et_bins, eta_bins)

# 3. Add to Tool Service and Run
ToolSvc += dumper
loop.run(1000) # Process 1000 events
```

---

## 📂 Project Structure

```text
trig-egamma-frame/
├── trig_egamma_frame/    # Main package code
│   ├── kernel/          # Core framework logic (Algorithm, StoreGate)
│   ├── emulator/        # Trigger step emulation (L1, L2, EF)
│   ├── algorithms/      # Processing algorithms (Filters, Dumpers)
│   ├── dataframe/       # EDM implementation and Menu helpers
│   ├── event/           # High-level Event Loop managers
│   └── enumerators.py   # System-wide Enums and Flags
├── share/               # Resource files
│   └── examples/        # Production-ready example scripts
├── scripts/             # Utility scripts for maintenance
├── images/              # Docker and container build files
├── Makefile             # Automation for builds and image management
└── setup.py             # Package installation script
```

---



## 📏 Coding Guidelines

> [!WARNING]
> To maintain consistency across the codebase, all developers must follow these naming conventions:
>
> - 📁 **Directories**: Must be all lowercase and use `snake_case`. (e.g., use `data_loader/` instead of `dataLoader/` or `DataLoader/`).
> - 🐍 **Python Files**: Must be all lowercase and use `snake_case`. (e.g., use `signal_processor.py` instead of `SignalProcessor.py` or `signalProcessor.py`).
> - ⚙️ **Methods and Functions**: Must use `snake_case`. (e.g., `def calculate_metrics():` instead of `def CalculateMetrics():`).
> - 🏛️ **Classes**: Must use `PascalCase` (also known as CamelCase). (e.g., `class DataIngestion:`).
>
> Always prioritize readability and adhere to PEP 8 standards where applicable.


---

## 📜 License

This project is licensed under the **GNU General Public License v3.0**.

---

<p align="center">
  <b>Developed by the Ringer UFRJ Group</b> 🎓 <br>
  <i>"Fast Egamma Trigger Emulation for ATLAS"</i>
</p>
