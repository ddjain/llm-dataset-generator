.PHONY: install run clean consolidate help

# Configuration
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
SRC_DIR := src
SCRIPTS_DIR := scripts
CONFIG_DIR := config
OUTPUT_DIR := output
TEMPLATES_DIR := templates

# Configurable paths (can be overridden)
DATA_DIR ?= $(OUTPUT_DIR)

# Default target
help:
	@echo "Dataset Generator - Available commands:"
	@echo ""
	@echo "  make install     - Create virtual environment and install dependencies"
	@echo "  make run         - Run the dataset generation script"
	@echo "  make consolidate - Consolidate all JSONL files into one file"
	@echo "  make clean       - Remove generated files and cache"
	@echo "  make clean-all   - Full cleanup including virtual environment"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "Configuration:"
	@echo "  DATA_DIR         - Output directory (default: $(DATA_DIR))"
	@echo ""
	@echo "Environment variables:"
	@echo "  LLM_API_BASE     - LLM API endpoint (default: http://127.0.0.1:1234)"
	@echo "  MODEL_NAME       - Model name to use (default: local-model)"
	@echo "  INFO_WORKERS     - Number of worker threads (default: 1)"
	@echo ""
	@echo "Usage examples:"
	@echo "  make run /path/to/markdown/files"
	@echo "  make run /path/to/docs DATA_DIR=custom/output"
	@echo "  make consolidate DATA_DIR=custom/output"

install:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Installation complete. Virtual environment ready."

run:
	@if [ -z "$(filter-out run,$(MAKECMDGOALS))" ]; then \
		echo "Usage: make run <source_path> [DATA_DIR=output_path]"; \
		echo "Example: make run /path/to/markdown/files"; \
		exit 1; \
	fi
	@SOURCE_PATH="$(filter-out run,$(MAKECMDGOALS))"; \
	if [ ! -d "$$SOURCE_PATH" ]; then \
		echo "Error: Source directory '$$SOURCE_PATH' does not exist"; \
		exit 1; \
	fi; \
	echo "Running dataset generation..."; \
	echo "Source directory: $$SOURCE_PATH"; \
	echo "Output directory: $(DATA_DIR)"; \
	mkdir -p $(DATA_DIR); \
	$(PYTHON) $(SRC_DIR)/summarize_information.py --source "$$SOURCE_PATH" --output $(DATA_DIR)

# Prevent make from treating the source path as a target
%:
	@:

consolidate:
	@echo "Consolidating JSONL files..."
	@if [ ! -d "$(DATA_DIR)" ]; then \
		echo "Error: Data directory '$(DATA_DIR)' not found. Run 'make run' first."; \
		exit 1; \
	fi
	$(SCRIPTS_DIR)/consolidate_jsonl.sh $(DATA_DIR) documentation_instruct.jsonl
	@echo "Consolidated file created: documentation_instruct.jsonl"

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ $(SRC_DIR)/__pycache__
	rm -f *.jsonl
	rm -rf logs/*.json
	@echo "Cleanup complete."

clean-all: clean
	@echo "Removing virtual environment and output..."
	rm -rf $(VENV_DIR)
	rm -rf $(OUTPUT_DIR)
	@echo "Full cleanup complete."
