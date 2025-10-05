#!/usr/bin/env bash
# =============================================================================
# Stelvio Simulation Quick Start Script
# =============================================================================
# 
# This script helps you quickly run simulations with common configurations.
# 
# Usage:
#   ./quickstart.sh [option]
#
# Options:
#   build          - Build the scenario
#   run            - Run all configurations
#   analyze        - Run data analysis
#   gui            - Launch GUI
#   export-csv     - Export results to CSV
#   clean          - Clean results
#   help           - Show this help
# =============================================================================

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCENARIO_DIR="$SCRIPT_DIR"
ARTERY_ROOT="/workspaces/artery"
BUILD_TOOL="$ARTERY_ROOT/tools/build.py"
RUN_TOOL="$ARTERY_ROOT/tools/run_artery.py"
VENV_DIR="$SCENARIO_DIR/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found! Run: make install-deps"
        exit 1
    fi
    source "$VENV_DIR/bin/activate"
}

check_build() {
    if [ ! -f "$ARTERY_ROOT/build/Release/scenarios/stelvio/libartery_stelvio.so" ]; then
        print_error "Scenario not built! Run: ./quickstart.sh build"
        exit 1
    fi
}

# =============================================================================
# Build Functions
# =============================================================================

build_scenario() {
    print_header "Building Stelvio Scenario using build.py"
    
    if [ ! -f "$BUILD_TOOL" ]; then
        print_error "Build tool not found: $BUILD_TOOL"
        exit 1
    fi
    
    cd "$ARTERY_ROOT"
    
    print_info "Running build.py configure and build..."
    python3 "$BUILD_TOOL" -cb --config Release
    
    print_success "Build complete!"
}

# =============================================================================
# Simulation Functions
# =============================================================================

run_simulation() {
    local CONFIG=$1
    local WITNESS_DELAY=${2:-5.0}
    
    print_info "Running configuration: $CONFIG"
    
    export STELVIO_WITNESS_DELAY=$WITNESS_DELAY
    
    cd "$SCENARIO_DIR"
    
    # Use run_artery.py tool
    python3 "$RUN_TOOL" \
        --launch-conf "$ARTERY_ROOT/build/Release" \
        --scenario "$SCENARIO_DIR" \
        -- \
        -u Cmdenv \
        -c "$CONFIG"
    
    print_success "Simulation $CONFIG completed"
}

run_crashed_scenarios() {
    print_header "Running Crashed Scenarios"
    check_build
    
    run_simulation "Crashed_Terrestrial"
    run_simulation "Crashed_Satellite"
    run_simulation "Crashed_Hybrid"
    
    print_success "All crashed scenarios completed!"
}

run_witness_scenarios() {
    print_header "Running Witness Scenarios"
    check_build
    
    local DELAY=${1:-3.0}
    print_info "Using witness delay: ${DELAY}s"
    
    run_simulation "Witness_Terrestrial" "$DELAY"
    run_simulation "Witness_Satellite" "$DELAY"
    run_simulation "Witness_Hybrid" "$DELAY"
    
    print_success "All witness scenarios completed!"
}

run_all_scenarios() {
    print_header "Running All Scenarios"
    run_crashed_scenarios
    run_witness_scenarios
    print_success "All simulations completed!"
}

# =============================================================================
# Analysis Functions
# =============================================================================

run_analysis() {
    print_header "Running Data Analysis"
    
    if [ ! -d "$SCENARIO_DIR/results" ] || [ -z "$(ls -A $SCENARIO_DIR/results)" ]; then
        print_error "No results found! Run simulations first."
        exit 1
    fi
    
    activate_venv
    
    cd "$SCENARIO_DIR"
    
    python3 analysis/analyze_results.py
    
    print_success "Analysis complete! Check analysis/plots/ for graphs"
}

launch_gui() {
    print_header "Launching Simulation GUI"
    
    activate_venv
    
    cd "$SCENARIO_DIR"
    python3 scripts/simulation_gui.py
}

export_csv() {
    print_header "Exporting Results to CSV"
    
    activate_venv
    
    cd "$SCENARIO_DIR"
    python3 scripts/export_csv.py --all
    
    print_success "CSV export complete!"
}

clean_results() {
    print_header "Cleaning Results"
    
    read -p "This will delete all simulation results. Continue? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$SCENARIO_DIR/results/"*
        rm -rf "$SCENARIO_DIR/analysis/csv_exports/"*
        rm -rf "$SCENARIO_DIR/analysis/plots/"*
        print_success "Results cleaned"
    else
        print_info "Cancelled"
    fi
}

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << EOF
Stelvio V2X Simulation - Quick Start Script

Usage: ./quickstart.sh [option]

Options:
  build          Build the scenario
  run            Run all configurations
  analyze        Run data analysis and generate plots
  gui            Launch graphical user interface
  export-csv     Export results to CSV format
  clean          Clean all results
  help           Show this help message

Examples:
  ./quickstart.sh build
  ./quickstart.sh run
  ./quickstart.sh analyze
  ./quickstart.sh gui

Environment Variables:
  STELVIO_WITNESS_DELAY    Witness reporting delay in seconds (default: 3.0)

For more information, see README.md
EOF
}

# =============================================================================
# Main
# =============================================================================

main() {
    case "${1:-help}" in
        build)
            build_scenario
            ;;
        run)
            run_all_scenarios
            ;;
        analyze)
            run_analysis
            ;;
        gui)
            launch_gui
            ;;
        export-csv)
            export_csv
            ;;
        clean)
            clean_results
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

main "$@"
