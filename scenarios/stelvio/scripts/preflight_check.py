#!/usr/bin/env python3
"""
Stelvio Scenario - Pre-flight Check
====================================

Verifies that all dependencies and files are in place before running simulations.
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util

# ANSI colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

SCENARIO_DIR = Path(__file__).parent.parent


def print_header(text):
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'='*80}{NC}")


def print_ok(text):
    print(f"{GREEN}✓{NC} {text}")


def print_fail(text):
    print(f"{RED}✗{NC} {text}")


def print_warn(text):
    print(f"{YELLOW}⚠{NC} {text}")


def check_file(file_path, description):
    """Check if a file exists"""
    if file_path.exists():
        print_ok(f"{description}: {file_path.name}")
        return True
    else:
        print_fail(f"{description} NOT FOUND: {file_path}")
        return False


def check_command(cmd, description):
    """Check if a command is available"""
    try:
        result = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
        print_ok(f"{description}: {cmd} found")
        return True
    except FileNotFoundError:
        print_fail(f"{description}: {cmd} NOT FOUND")
        return False
    except subprocess.TimeoutExpired:
        print_warn(f"{description}: {cmd} found but slow to respond")
        return True


def check_python_package(package_name, description):
    """Check if a Python package is installed"""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        print_ok(f"{description}: {package_name}")
        return True
    else:
        print_fail(f"{description}: {package_name} NOT INSTALLED")
        return False


def main():
    print_header("Stelvio Scenario - Pre-flight Check")
    print()
    
    checks_passed = []
    checks_failed = []
    
    # =========================================================================
    # 1. Check Scenario Files
    # =========================================================================
    print(f"{BLUE}[1/6] Checking scenario files...{NC}")
    
    files_to_check = [
        (SCENARIO_DIR / "omnetpp.ini", "OMNeT++ configuration"),
        (SCENARIO_DIR / "CMakeLists.txt", "Build configuration"),
        (SCENARIO_DIR / "stelvio.sumocfg", "SUMO configuration"),
        (SCENARIO_DIR / "stelvio.net.xml", "SUMO network"),
        (SCENARIO_DIR / "stelvio.rou.xml", "SUMO routes"),
        (SCENARIO_DIR / "static_nodes.xml", "Static nodes"),
        (SCENARIO_DIR / "crash_storyboard.py", "Crash storyboard"),
        (SCENARIO_DIR / "witness_storyboard.py", "Witness storyboard"),
    ]
    
    for file_path, desc in files_to_check:
        if check_file(file_path, desc):
            checks_passed.append(desc)
        else:
            checks_failed.append(desc)
    
    print()
    
    # =========================================================================
    # 2. Check C++ Source Files
    # =========================================================================
    print(f"{BLUE}[2/6] Checking C++ source files...{NC}")
    
    src_files = [
        (SCENARIO_DIR / "src/DenmMessage.msg", "DENM message"),
        (SCENARIO_DIR / "src/CrashedVehicleService.h", "CrashedVehicleService header"),
        (SCENARIO_DIR / "src/CrashedVehicleService.cc", "CrashedVehicleService impl"),
        (SCENARIO_DIR / "src/WitnessVehicleService.h", "WitnessVehicleService header"),
        (SCENARIO_DIR / "src/WitnessVehicleService.cc", "WitnessVehicleService impl"),
        (SCENARIO_DIR / "src/InfrastructureService.h", "InfrastructureService header"),
        (SCENARIO_DIR / "src/InfrastructureService.cc", "InfrastructureService impl"),
        (SCENARIO_DIR / "src/VehicleReceiverService.h", "VehicleReceiverService header"),
        (SCENARIO_DIR / "src/VehicleReceiverService.cc", "VehicleReceiverService impl"),
    ]
    
    for file_path, desc in src_files:
        if check_file(file_path, desc):
            checks_passed.append(desc)
        else:
            checks_failed.append(desc)
    
    print()
    
    # =========================================================================
    # 3. Check Configuration Files
    # =========================================================================
    print(f"{BLUE}[3/6] Checking configuration files...{NC}")
    
    config_files = [
        (SCENARIO_DIR / "config/services_crashed.xml", "Crashed services"),
        (SCENARIO_DIR / "config/services_witness.xml", "Witness services"),
        (SCENARIO_DIR / "config/services_infrastructure.xml", "Infrastructure services"),
    ]
    
    for file_path, desc in config_files:
        if check_file(file_path, desc):
            checks_passed.append(desc)
        else:
            checks_failed.append(desc)
    
    print()
    
    # =========================================================================
    # 4. Check Scripts
    # =========================================================================
    print(f"{BLUE}[4/6] Checking scripts...{NC}")
    
    scripts = [
        (SCENARIO_DIR / "scripts/simulation_gui.py", "Simulation GUI"),
        (SCENARIO_DIR / "scripts/export_csv.py", "CSV export script"),
        (SCENARIO_DIR / "analysis/analyze_results.py", "Analysis script"),
        (SCENARIO_DIR / "quickstart.sh", "Quick start script"),
    ]
    
    for file_path, desc in scripts:
        if check_file(file_path, desc):
            checks_passed.append(desc)
            # Check if executable
            if file_path.suffix in ['.py', '.sh'] and not os.access(file_path, os.X_OK):
                print_warn(f"  {file_path.name} is not executable (run: chmod +x {file_path})")
        else:
            checks_failed.append(desc)
    
    print()
    
    # =========================================================================
    # 5. Check System Dependencies
    # =========================================================================
    print(f"{BLUE}[5/6] Checking system dependencies...{NC}")
    
    commands = [
        ("cmake", "CMake"),
        ("make", "Make"),
        ("opp_run", "OMNeT++"),
        ("sumo", "SUMO"),
        ("python3", "Python 3"),
    ]
    
    for cmd, desc in commands:
        if check_command(cmd, desc):
            checks_passed.append(desc)
        else:
            checks_failed.append(desc)
    
    print()
    
    # =========================================================================
    # 6. Check Python Dependencies
    # =========================================================================
    print(f"{BLUE}[6/6] Checking Python packages...{NC}")
    
    packages = [
        ("PyQt5", "PyQt5 (for GUI)"),
        ("pandas", "Pandas (for analysis)"),
        ("matplotlib", "Matplotlib (for plots)"),
        ("seaborn", "Seaborn (for plots)"),
        ("numpy", "NumPy (for analysis)"),
    ]
    
    for pkg, desc in packages:
        if check_python_package(pkg, desc):
            checks_passed.append(desc)
        else:
            checks_failed.append(desc)
            if pkg == "PyQt5":
                print(f"      Install with: pip install PyQt5")
            elif pkg in ["pandas", "matplotlib", "seaborn", "numpy"]:
                print(f"      Install with: pip install {pkg}")
    
    print()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print_header("Summary")
    print()
    print(f"{GREEN}Passed:{NC} {len(checks_passed)}")
    print(f"{RED}Failed:{NC} {len(checks_failed)}")
    print()
    
    if checks_failed:
        print(f"{RED}The following checks failed:{NC}")
        for item in checks_failed[:10]:  # Show first 10
            print(f"  • {item}")
        if len(checks_failed) > 10:
            print(f"  ... and {len(checks_failed) - 10} more")
        print()
        print(f"{YELLOW}Please resolve these issues before running simulations.{NC}")
        print()
        return 1
    else:
        print(f"{GREEN}✅ All checks passed! You're ready to run simulations.{NC}")
        print()
        print("Next steps:")
        print("  1. Build:    ./quick_start.sh build")
        print("  2. Run:      ./quick_start.sh run-crashed")
        print("  3. Analyze:  ./quick_start.sh analyze")
        print("  OR")
        print("  Launch GUI:  python3 scripts/simulation_gui.py")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
