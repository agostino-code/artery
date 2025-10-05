#!/usr/bin/env python3
"""
Export Stelvio Simulation Results to CSV
=========================================

Exports OMNeT++ .sca files to CSV format for external analysis.

Features:
- Handles multiple repetitions per configuration
- Groups by scenario type (Crashed/Witness) and infrastructure (Terrestrial/Satellite/Hybrid)
- Exports raw data and aggregated statistics
- Supports selective or full export

Usage:
    python3 export_csv.py --all                    # Export all configurations
    python3 export_csv.py --crashed               # Only crashed scenarios
    python3 export_csv.py --witness               # Only witness scenarios
    python3 export_csv.py --config Crashed_Hybrid # Specific configuration
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

# =============================================================================
# Configuration
# =============================================================================

SCENARIO_DIR = Path(__file__).parent.parent
RESULTS_DIR = SCENARIO_DIR / "results"
CSV_EXPORT_DIR = SCENARIO_DIR / "analysis" / "csv"

# Configuration mapping
CONFIGURATIONS = {
    "Crashed": ["Crashed_Terrestrial", "Crashed_Satellite", "Crashed_Hybrid"],
    "Witness": ["Witness_Terrestrial", "Witness_Satellite", "Witness_Hybrid"],
}

ALL_CONFIGS = CONFIGURATIONS["Crashed"] + CONFIGURATIONS["Witness"]


# =============================================================================
# SCA File Parser
# =============================================================================

class SCAParser:
    """Parse OMNeT++ .sca scalar files"""
    
    def __init__(self, sca_file: Path):
        self.sca_file = sca_file
        self.scalars = []
        self.run_info = {}
    
    def parse(self) -> pd.DataFrame:
        """Parse .sca file and return DataFrame"""
        with open(self.sca_file, 'r') as f:
            current_run = None
            
            for line in f:
                line = line.strip()
                
                # Parse run declaration
                if line.startswith("run"):
                    match = re.match(r'run\s+(.+)', line)
                    if match:
                        current_run = match.group(1)
                
                # Parse scalar
                elif line.startswith("scalar"):
                    parts = line.split()
                    if len(parts) >= 4:
                        module = parts[1]
                        scalar_name = parts[2]
                        value = parts[3]
                        
                        try:
                            value_float = float(value)
                            self.scalars.append({
                                'run': current_run,
                                'module': module,
                                'scalar': scalar_name,
                                'value': value_float
                            })
                        except ValueError:
                            continue
        
        return pd.DataFrame(self.scalars)


# =============================================================================
# Result Aggregator
# =============================================================================

class ResultAggregator:
    """Aggregate results from multiple repetitions"""
    
    def __init__(self, config_name: str):
        self.config_name = config_name
        self.repetitions = []
        self.raw_data = []
    
    def add_repetition(self, rep_num: int, df: pd.DataFrame):
        """Add data from one repetition"""
        df['repetition'] = rep_num
        self.repetitions.append(rep_num)
        self.raw_data.append(df)
    
    def get_raw_dataframe(self) -> pd.DataFrame:
        """Get combined raw data from all repetitions"""
        if not self.raw_data:
            return pd.DataFrame()
        return pd.concat(self.raw_data, ignore_index=True)
    
    def get_aggregated_stats(self) -> pd.DataFrame:
        """Calculate statistics across repetitions"""
        if not self.raw_data:
            return pd.DataFrame()
        
        combined = self.get_raw_dataframe()
        
        # Group by module and scalar, calculate statistics
        stats = combined.groupby(['module', 'scalar'])['value'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max'),
            ('count', 'count')
        ]).reset_index()
        
        stats['config'] = self.config_name
        stats['repetitions'] = len(self.repetitions)
        
        return stats
    
    def get_vehicle_metrics(self) -> pd.DataFrame:
        """Extract per-vehicle metrics"""
        if not self.raw_data:
            return pd.DataFrame()
        
        combined = self.get_raw_dataframe()
        
        # Filter vehicle-related metrics
        vehicle_metrics = combined[combined['module'].str.contains('node\\[')]
        
        return vehicle_metrics
    
    def get_infrastructure_metrics(self) -> pd.DataFrame:
        """Extract infrastructure metrics"""
        if not self.raw_data:
            return pd.DataFrame()
        
        combined = self.get_raw_dataframe()
        
        # Filter infrastructure metrics
        infra_metrics = combined[
            combined['module'].str.contains('antenna|satellite', case=False)
        ]
        
        return infra_metrics


# =============================================================================
# Export Manager
# =============================================================================

class ExportManager:
    """Manage CSV export operations"""
    
    def __init__(self):
        self.aggregators: Dict[str, ResultAggregator] = {}
        CSV_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    def scan_results(self, config_name: str) -> int:
        """Scan results directory for a configuration"""
        config_dir = RESULTS_DIR / config_name.lower()
        
        if not config_dir.exists():
            print(f"  ⚠️  No results found for {config_name}")
            return 0
        
        # Find all .sca files
        sca_files = sorted(config_dir.glob("*.sca"))
        
        if not sca_files:
            print(f"  ⚠️  No .sca files found in {config_dir}")
            return 0
        
        aggregator = ResultAggregator(config_name)
        
        for idx, sca_file in enumerate(sca_files, start=1):
            print(f"    Parsing repetition {idx}: {sca_file.name}")
            parser = SCAParser(sca_file)
            df = parser.parse()
            aggregator.add_repetition(idx, df)
        
        self.aggregators[config_name] = aggregator
        return len(sca_files)
    
    def export_configuration(self, config_name: str):
        """Export all data for one configuration"""
        if config_name not in self.aggregators:
            print(f"  ⚠️  No data loaded for {config_name}")
            return
        
        aggregator = self.aggregators[config_name]
        
        # Export raw data
        raw_df = aggregator.get_raw_dataframe()
        if not raw_df.empty:
            raw_file = CSV_EXPORT_DIR / f"{config_name}_raw.csv"
            raw_df.to_csv(raw_file, index=False)
            print(f"    ✓ Raw data: {raw_file.name} ({len(raw_df)} rows)")
        
        # Export aggregated statistics
        stats_df = aggregator.get_aggregated_stats()
        if not stats_df.empty:
            stats_file = CSV_EXPORT_DIR / f"{config_name}_stats.csv"
            stats_df.to_csv(stats_file, index=False)
            print(f"    ✓ Statistics: {stats_file.name} ({len(stats_df)} metrics)")
        
        # Export vehicle metrics
        vehicle_df = aggregator.get_vehicle_metrics()
        if not vehicle_df.empty:
            vehicle_file = CSV_EXPORT_DIR / f"{config_name}_vehicles.csv"
            vehicle_df.to_csv(vehicle_file, index=False)
            print(f"    ✓ Vehicle metrics: {vehicle_file.name}")
        
        # Export infrastructure metrics
        infra_df = aggregator.get_infrastructure_metrics()
        if not infra_df.empty:
            infra_file = CSV_EXPORT_DIR / f"{config_name}_infrastructure.csv"
            infra_df.to_csv(infra_file, index=False)
            print(f"    ✓ Infrastructure metrics: {infra_file.name}")
    
    def export_comparison(self, config_names: List[str]):
        """Export comparison table across configurations"""
        if not self.aggregators:
            return
        
        all_stats = []
        for config_name in config_names:
            if config_name in self.aggregators:
                stats = self.aggregators[config_name].get_aggregated_stats()
                all_stats.append(stats)
        
        if not all_stats:
            return
        
        # Combine all statistics
        comparison_df = pd.concat(all_stats, ignore_index=True)
        
        # Pivot for easier comparison
        pivot_df = comparison_df.pivot_table(
            index=['module', 'scalar'],
            columns='config',
            values='mean',
            aggfunc='first'
        )
        
        comparison_file = CSV_EXPORT_DIR / "comparison_all_configs.csv"
        pivot_df.to_csv(comparison_file)
        print(f"\n  ✓ Comparison table: {comparison_file.name}")
    
    def export_summary_table(self, config_names: List[str]):
        """Export summary table with key metrics"""
        summary_data = []
        
        for config_name in config_names:
            if config_name not in self.aggregators:
                continue
            
            aggregator = self.aggregators[config_name]
            stats = aggregator.get_aggregated_stats()
            
            # Extract key metrics
            row = {
                'Configuration': config_name,
                'Repetitions': len(aggregator.repetitions),
            }
            
            # Reception delay
            delay_metric = stats[stats['scalar'].str.contains('reception_delay', case=False)]
            if not delay_metric.empty:
                row['Mean_Reception_Delay_ms'] = delay_metric['mean'].mean() * 1000
                row['Median_Reception_Delay_ms'] = delay_metric['median'].mean() * 1000
            
            # Cloud delivery latency
            cloud_metric = stats[stats['scalar'].str.contains('cloud_delivery_latency', case=False)]
            if not cloud_metric.empty:
                row['Mean_Cloud_Latency_ms'] = cloud_metric['mean'].mean() * 1000
            
            # Packet delivery ratio (estimate from received flags)
            received_metric = stats[stats['scalar'].str.contains('received_flag', case=False)]
            if not received_metric.empty:
                row['PDR_%'] = received_metric['mean'].mean() * 100
            
            # Coverage
            coverage_metric = stats[stats['scalar'].str.contains('in_coverage', case=False)]
            if not coverage_metric.empty:
                row['Coverage_%'] = (coverage_metric['mean'].sum() / coverage_metric['count'].sum()) * 100
            
            summary_data.append(row)
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_file = CSV_EXPORT_DIR / "summary_statistics.csv"
            summary_df.to_csv(summary_file, index=False)
            print(f"\n  ✓ Summary table: {summary_file.name}")
            
            # Print summary
            print("\n" + "="*80)
            print("SUMMARY STATISTICS")
            print("="*80)
            print(summary_df.to_string(index=False))
            print("="*80)


# =============================================================================
# Main Export Function
# =============================================================================

def export_results(config_names: List[str]):
    """Export results for specified configurations"""
    print("\n" + "="*80)
    print("STELVIO RESULTS EXPORT")
    print("="*80)
    
    # Clean previous exports
    print("\n🗑️  Cleaning previous exports...")
    if CSV_EXPORT_DIR.exists():
        for file in CSV_EXPORT_DIR.glob("*.csv"):
            file.unlink()
        print(f"  ✓ Removed old CSV files from {CSV_EXPORT_DIR}")
    
    manager = ExportManager()
    
    # Scan and load data
    print("\n📂 Scanning results...")
    for config_name in config_names:
        print(f"\n  {config_name}:")
        num_reps = manager.scan_results(config_name)
        if num_reps > 0:
            print(f"    ✓ Found {num_reps} repetitions")
    
    # Export individual configurations
    print("\n📊 Exporting data...")
    for config_name in config_names:
        print(f"\n  {config_name}:")
        manager.export_configuration(config_name)
    
    # Export comparison
    print("\n📈 Generating comparisons...")
    manager.export_comparison(config_names)
    manager.export_summary_table(config_names)
    
    print("\n" + "="*80)
    print(f"✓ Export complete! Files saved to: {CSV_EXPORT_DIR}")
    print("="*80 + "\n")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Export Stelvio simulation results to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                      Export all configurations
  %(prog)s --crashed                  Export only crashed scenarios
  %(prog)s --witness                  Export only witness scenarios
  %(prog)s --config Crashed_Hybrid    Export specific configuration
        """
    )
    
    parser.add_argument('--all', action='store_true',
                        help='Export all configurations')
    parser.add_argument('--crashed', action='store_true',
                        help='Export crashed scenarios only')
    parser.add_argument('--witness', action='store_true',
                        help='Export witness scenarios only')
    parser.add_argument('--config', type=str,
                        help='Export specific configuration')
    
    args = parser.parse_args()
    
    # Determine which configurations to export
    configs_to_export = []
    
    if args.all:
        configs_to_export = ALL_CONFIGS
    elif args.crashed:
        configs_to_export = CONFIGURATIONS["Crashed"]
    elif args.witness:
        configs_to_export = CONFIGURATIONS["Witness"]
    elif args.config:
        if args.config in ALL_CONFIGS:
            configs_to_export = [args.config]
        else:
            print(f"❌ Error: Unknown configuration '{args.config}'")
            print(f"Available configurations: {', '.join(ALL_CONFIGS)}")
            sys.exit(1)
    else:
        # Default: export all
        configs_to_export = ALL_CONFIGS
    
    # Export
    export_results(configs_to_export)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
