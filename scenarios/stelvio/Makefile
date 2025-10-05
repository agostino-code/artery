# Makefile for Stelvio V2X Simulation
# =============================================================================
# Quick commands:
#   make help          - Show available commands
#   make install-deps  - Install Python dependencies
#   make check         - Run preflight checks
#   make build         - Build the scenario
#   make run-crashed   - Run crashed scenarios
#   make run-witness   - Run witness scenarios
#   make analyze       - Analyze results
#   make gui           - Launch GUI
#   make clean         - Clean results
# =============================================================================

.PHONY: help install-deps check build run analyze gui export-csv clean

# Default target
.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Paths
SCENARIO_DIR := $(shell pwd)
ARTERY_ROOT := /workspaces/artery
BUILD_TOOL := $(ARTERY_ROOT)/tools/build.py
RUN_TOOL := $(ARTERY_ROOT)/tools/run_artery.py
VENV_DIR := $(SCENARIO_DIR)/venv

help: ## Show this help message
	@printf '%b\n' "$(BLUE)Stelvio V2X Simulation - Makefile$(NC)"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  1. make install-deps"
	@echo "  2. make check"
	@echo "  3. make build"
	@echo "  4. make run"
	@echo "  5. make analyze"
	@echo ""

install-deps: ## Install Python dependencies
	@printf '%b\n' "$(BLUE)Installing Python dependencies...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
	fi
	@$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel
	@$(VENV_DIR)/bin/pip install -r requirements.txt
	@printf '%b\n' "$(GREEN)✓ Dependencies installed in venv$(NC)"

check: ## Run preflight checks
	@printf '%b\n' "$(BLUE)Running preflight checks...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
	printf '%b\n' "$(YELLOW)Virtual environment not found. Run: make install-deps$(NC)"; \
		exit 1; \
	fi
	@$(VENV_DIR)/bin/python3 scripts/preflight_check.py

build: ## Build the scenario
	@printf '%b\n' "$(BLUE)Building Stelvio scenario using build.py...$(NC)"
	cd $(ARTERY_ROOT) && python3 $(BUILD_TOOL) -cb --config Release
	@printf '%b\n' "$(GREEN)✓ Build complete$(NC)"


run: ## Clean and run all scenarios (clean + run)
	@printf '%b\n' "$(BLUE)Cleaning and running all scenarios...$(NC)"
	$(MAKE) clean
	@printf '%b\n' "$(BLUE)Running all scenarios...$(NC)"
	./quickstart.sh run

analyze: ## Analyze simulation results
	@printf '%b\n' "$(BLUE)Analyzing results...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
	printf '%b\n' "$(YELLOW)Virtual environment not found. Run: make install-deps$(NC)"; \
		exit 1; \
	fi
	@$(VENV_DIR)/bin/python3 analysis/analyze_results.py

gui: ## Launch simulation GUI
	@printf '%b\n' "$(BLUE)Launching GUI...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
	printf '%b\n' "$(YELLOW)Virtual environment not found. Run: make install-deps$(NC)"; \
		exit 1; \
	fi
	@$(VENV_DIR)/bin/python3 scripts/simulation_gui.py

export-csv: ## Export results to CSV
	@printf '%b\n' "$(BLUE)Exporting to CSV...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
	printf '%b\n' "$(YELLOW)Virtual environment not found. Run: make install-deps$(NC)"; \
		exit 1; \
	fi
	@$(VENV_DIR)/bin/python3 scripts/export_csv.py --all

clean: ## Clean simulation results, CSV exports and analysis plots
	@printf '%b\n' "$(YELLOW)Cleaning results, CSV exports and analysis plots...$(NC)"
	# Remove simulation results
	rm -rf results/*/
	# Remove CSV exports created by export_csv.py
	rm -rf analysis/csv_exports/* || true
	# Remove analysis CSV summaries (some tools write to analysis/csv)
	rm -rf analysis/csv/* || true
	# Remove generated plots
	rm -rf analysis/plots/* || true
	# Remove any leftover config-specific directories (safe-guard)
	rm -rf Crashed_* Witness_* || true
	@printf '%b\n' "$(GREEN)✓ Results, CSVs and plots cleaned$(NC)"

clean-all: clean ## Clean results and build artifacts
	@printf '%b\n' "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -f libstelvio.so
	rm -rf src/*.o
	@printf '%b\n' "$(GREEN)✓ All cleaned$(NC)"

test: ## Run a quick test simulation
	@printf '%b\n' "$(BLUE)Running quick test...$(NC)"
	cd $(SCENARIO_DIR) && \
	opp_run -u Cmdenv -c Crashed_Terrestrial \
		--sim-time-limit=100s \
		-n src:. -l libstelvio.so omnetpp.ini
	@printf '%b\n' "$(GREEN)✓ Test complete$(NC)"

list-configs: ## List available configurations
	@printf '%b\n' "$(BLUE)Available configurations:$(NC)"
	@echo "  • Crashed_Terrestrial"
	@echo "  • Crashed_Satellite"
	@echo "  • Crashed_Hybrid"
	@echo "  • Witness_Terrestrial"
	@echo "  • Witness_Satellite"
	@echo "  • Witness_Hybrid"

info: ## Show project information
	@printf '%b\n' "$(BLUE)Stelvio V2X Simulation$(NC)"
	@echo ""
	@echo "Scenario directory: $(SCENARIO_DIR)"
	@echo "Build directory:    $(BUILD_DIR)"
	@echo ""
	@echo "Files:"
	@find . -type f \( -name "*.cc" -o -name "*.h" -o -name "*.msg" \) | wc -l | xargs echo "  C++ source files:"
	@find . -type f -name "*.py" | wc -l | xargs echo "  Python scripts:  "
	@find . -type f -name "*.xml" | wc -l | xargs echo "  XML config files:"
	@echo ""
	@if [ -d "results" ]; then \
		find results -name "*.sca" | wc -l | xargs echo "  Result files (.sca):"; \
	fi
	@echo ""
	@echo "For more info: make help"
