# ⚡ trig_egamma_frame

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Framework: ROOT](https://img.shields.io/badge/ROOT-6.xx-orange.svg)](https://root.cern/)

A high-performance framework for **ATLAS Trigger Egamma emulation** and data processing. Designed for Run 3, this framework provides a modular and efficient environment to simulate trigger chains, optimize selectors (like Ringer), and dump analysis-ready data.

---

## 🌟 Key Features

- **🚀 Run 3 Emulation**: Complete emulation of L1 Calo, L2 Calo (FastCalo), Fast Electron, and Precision steps.
- **🧠 ML-Ready**: Built-in support for the **Ringer Selector** using TensorFlow/Keras and ONNX.
- **🏗️ Modular Architecture**: Leverages `Algorithm`, `StoreGate`, and `EDM` patterns for clean, extensible code.
- **📊 Fast Data Dumping**: Integrated `ElectronDumper` utilizing ROOT's `RDataFrame` (FromNumpy) for high-speed I/O.
- **🐳 Container Support**: Optimized for execution within Singularity/Apptainer environments.

---

## 🛠️ Getting Started

### 1. Requirements

This project heavily relies on **CERN ROOT** and **TensorFlow**. It is highly recommended to run this within the provided Singularity container.

### 2. Environment Setup

Clone the repository and initialize the environment:

```bash
git clone https://github.com/ringer-ufrj-br/trig-egamma-frame.git
cd trig-egamma-frame
source activate.sh
```

The `activate.sh` script will:
- Check for a virtual environment in `.trig_egamma_frame-env`.
- Create and install dependencies if missing.
- Set up necessary environment variables (e.g., `LOGURU_LEVEL`, `CERN_DATA`).

### 3. Running with Singularity

If you are on a cluster, use the provided `Makefile` to pull and run the environment:

```bash
# Run the container
singularity run --bind /mnt/shared:/mnt/shared root_image.sif
```

---

## 📂 Project Structure

```text
trig_egamma_frame/
├── kernel/            # Core framework (Algorithm, StoreGate, StatusCode)
├── emulator/          # Trigger emulation logic (L1, L2, EF steps)
│   └── run3/          # Run 3 specific implementations (Selector, Menu)
├── algorithms/        # High-level processing (Filter, Dumper)
├── event/             # Event Data Model (EDM) definitions
└── dataframe/         # Menu and configuration utilities
share/
└── examples/          # Reference scripts for common tasks
```

---

## 📈 Usage Example

To run a basic emulation and dump results, you can use the provided example script:

```python
from trig_egamma_frame import ElectronLoop, DataframeSchemma
from trig_egamma_frame.algorithms.dumper import ElectronDumper_v2 as ElectronDumper
from trig_egamma_frame.kernel import ToolSvc

# Configure the event loop
acc = ElectronLoop(
    "EventATLASLoop",
    inputFile  = "path/to/data",
    treePath   = "*/HLT/Physval/Egamma/probes",
    dataframe  = DataframeSchemma.Run2,
    outputFile = "output.root"
)

# Add a dumper algorithm
dumper = ElectronDumper("output_prefix", et_bins, eta_bins)
ToolSvc += dumper

# Run the processing
acc.run(1000)
```

For more complex configurations, check [share/examples/run.py](file:///home/joao.pinto/git_repos/trig-egamma-frame/share/examples/run.py).

---

## 🧪 Development & Testing

We use `loguru` for beautiful, informative logging. You can control the verbosity using:

```bash
export LOGURU_LEVEL=DEBUG
```

### Build & Deploy

Refer to the `Makefile` for container-related tasks:
- `make build`: Build the Docker image.
- `make push`: Push to registry.
- `make pull`: Convert/Pull to Singularity image.

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](http://www.gnu.org/licenses/gpl-3.0.html) for details.

---

<p align="center">
  Developed by the <b>Ringer UFRJ Group</b>
</p>
