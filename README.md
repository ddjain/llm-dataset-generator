# Dataset Generator

A tool for generating instruction-output JSONL datasets from Markdown documentation for LLM fine-tuning.

## Project Structure

```
dataset-generator/
├── src/                          # Source code
│   └── summarize_information.py  # Main dataset generation script
├── scripts/                      # Utility scripts
│   └── consolidate_jsonl.sh     # Script to consolidate JSONL files
├── config/                       # Configuration and input data
│   └── input/                    # Input data directory
│       └── website/              # Website content source
├── templates/                    # Template files
│   └── prompt.txt               # LLM prompt template
├── output/                       # Generated dataset output
├── logs/                         # Processing logs
├── venv/                         # Python virtual environment
├── requirements.txt              # Python dependencies
├── Makefile                      # Build automation
└── README.md                     # This file
```

## Quick Start

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Run dataset generation:**
   ```bash
   make run /path/to/markdown/files
   ```

3. **Consolidate generated files:**
   ```bash
   make consolidate
   ```

## Available Commands

- `make install` - Create virtual environment and install dependencies
- `make run` - Run the dataset generation script
- `make consolidate` - Consolidate all JSONL files into one file
- `make clean` - Remove generated files and cache
- `make clean-all` - Full cleanup including virtual environment and output
- `make help` - Show available commands

## Configuration

### Directory Paths (Makefile Variables)
- `DATA_DIR` - Output directory for generated data (default: `output`)

### Environment Variables
- `LLM_API_BASE` - LLM API endpoint (default: http://127.0.0.1:1234)
- `MODEL_NAME` - Model name to use (default: local-model)
- `INFO_WORKERS` - Number of worker threads (default: 1)

## Usage Examples

### Basic usage:
```bash
make install
make run /path/to/markdown/files
make consolidate
```

### With custom input/output directories:
```bash
make run /path/to/docs DATA_DIR=custom/output
make consolidate DATA_DIR=custom/output
```

### With custom configuration:
```bash
export LLM_API_BASE="http://localhost:8080"
export MODEL_NAME="my-custom-model"
make run
```

### Clean up after processing:
```bash
make clean        # Remove generated files only
make clean-all    # Remove everything including venv and output
```

## Direct Script Usage

You can also run the script directly with custom arguments:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run with custom paths
python src/summarize_information.py --source /path/to/docs --output /path/to/output

# Run with default paths
python src/summarize_information.py
```

## Output

The tool generates:
- Individual JSONL files in the output directory (mirroring input structure)
- Processing logs in the `logs/` directory
- A consolidated `documentation_instruct.jsonl` file when using `make consolidate`

## Requirements

- Python 3.7+
- jq (for JSONL consolidation)
- Local LLM API server running (default: localhost:1234)

## Customizing Templates

Edit `templates/prompt.txt` to customize the LLM prompt template used for generating instruction-output pairs.
