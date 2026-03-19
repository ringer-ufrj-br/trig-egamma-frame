SHELL := /bin/bash

# Load environment variables from activate.sh for use in Makefile
# This helps use variables like MLFLOW_PORT, etc. directly.
-include .env_vars

.PHONY: build jupyter build_root_image
all:  build

# Helper to export vars from activate.sh into a temporary file for Makefile inclusion
.env_vars: activate.sh
	@grep "export " activate.sh | sed 's/export //' > .env_vars

build: .env_vars
	@bash activate.sh

jupyter: .env_vars
	@bash activate.sh && jupyter lab --IdentityProvider.token="" --ServerApp.password=""

build_root_image:
	singularity build --fakeroot --force root_image.sif images/root/Singularity.def


clean:
	@echo "🧹 Cleaning up..."
	rm -rf .egamma-env
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✨ Done!"