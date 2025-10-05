#!/usr/bin/env python3
"""
Stelvio Simulation GUI - Simplified
====================================

Simple GUI for running Stelvio simulations using make commands.

Requirements:
    pip install PyQt5
"""

import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# =============================================================================
# Configuration
# =============================================================================

SCENARIO_DIR = Path(__file__).parent.parent

# =============================================================================
# Worker Thread
# =============================================================================

class MakeWorker(QThread):
    """Background thread for running make commands"""
    
    output = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, command: str):
        super().__init__()
        self.command = command
        self._running = True
    
    def stop(self):
        self._running = False
    
    def run(self):
        """Execute make command"""
        try:
            self.output.emit(f"\n▶ Running: make {self.command}\n")
            
            process = subprocess.Popen(
                ["make", self.command],
                cwd=SCENARIO_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output
            for line in process.stdout:
                if not self._running:
                    process.terminate()
                    self.finished.emit(False, "Cancelled by user")
                    return
                self.output.emit(line)
            
            process.wait()
            
            if process.returncode == 0:
                self.finished.emit(True, f"✓ Command completed successfully")
            else:
                self.finished.emit(False, f"✗ Command failed with exit code {process.returncode}")
                
        except Exception as e:
            self.finished.emit(False, f"✗ Error: {str(e)}")


# =============================================================================
# Main GUI
# =============================================================================

class StelvioGUI(QMainWindow):
    """Simplified Stelvio simulation GUI"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()
    
    def initUI(self):
        """Initialize user interface"""
        self.setWindowTitle("Stelvio V2X Simulation - Quick Control")
        self.setGeometry(150, 150, 900, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Stelvio V2X - 6G Hybrid Infrastructure Simulation")
        title_font = QFont("Arial", 16, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2196F3; padding: 15px;")
        layout.addWidget(title)
        
        # Info
        info = QLabel("Quick access to simulation commands via make")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #666; padding: 5px; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Build section
        build_group = QGroupBox("1. Build")
        build_layout = QVBoxLayout()
        
        build_btn = self._create_button("Build Scenario", "#4CAF50", "build")
        build_btn.clicked.connect(lambda: self.run_make("build"))
        build_layout.addWidget(build_btn)
        
        build_group.setLayout(build_layout)
        layout.addWidget(build_group)
        
        # Simulation section
        sim_group = QGroupBox("2. Run Simulations")
        sim_layout = QVBoxLayout()
        
        sim_info = QLabel("Run simulations with standard parameters (Witness delay: 3s)")
        sim_info.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        sim_layout.addWidget(sim_info)
        
        # single unified run only, individual run buttons removed
        
        all_btn = self._create_button("Run All Scenarios", "#9C27B0", "run")
        all_btn.clicked.connect(lambda: self.run_make("run"))
        sim_layout.addWidget(all_btn)
        
        sim_group.setLayout(sim_layout)
        layout.addWidget(sim_group)
        
        # Analysis section
        analysis_group = QGroupBox("3. Analysis & Export")
        analysis_layout = QVBoxLayout()

        analysis_info = QLabel("Generate plots and export real data to CSV")
        analysis_info.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        analysis_layout.addWidget(analysis_info)
        
        btn_row2 = QHBoxLayout()
        analyze_btn = self._create_button("Generate Plots", "#2196F3", "analyze")
        analyze_btn.clicked.connect(lambda: self.run_make("analyze"))
        btn_row2.addWidget(analyze_btn)
        
        export_btn = self._create_button("Export CSV", "#00BCD4", "export-csv")
        export_btn.clicked.connect(lambda: self.run_make("export-csv"))
        btn_row2.addWidget(export_btn)
        analysis_layout.addLayout(btn_row2)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Utilities section
        util_group = QGroupBox("4. Utilities")
        util_layout = QHBoxLayout()
        
        clean_btn = self._create_button("Clean Results", "#F44336", "clean")
        clean_btn.clicked.connect(self.clean_results)
        util_layout.addWidget(clean_btn)
        
        help_btn = self._create_button("Show Help", "#607D8B", "help")
        help_btn.clicked.connect(self.show_help)
        util_layout.addWidget(help_btn)
        
        util_group.setLayout(util_layout)
        layout.addWidget(util_group)
        
        # Stop button
        self.stop_btn = QPushButton("⏹ Stop Current Operation")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_operation)
        layout.addWidget(self.stop_btn)
        
        # Console output
        console_label = QLabel("Console Output:")
        console_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #00FF00;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
                border: 2px solid #444;
                border-radius: 5px;
            }
        """)
        self.console.setMinimumHeight(200)
        layout.addWidget(self.console)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.console.append("Ready. Select a command to begin.\n")
    
    def _create_button(self, text: str, color: str, tooltip: str) -> QPushButton:
        """Create a styled button"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }}
            QPushButton:hover {{
                opacity: 0.9;
                background-color: {color};
                filter: brightness(110%);
            }}
            QPushButton:pressed {{
                background-color: {color};
                padding-top: 14px;
                padding-bottom: 10px;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
            }}
        """)
        btn.setToolTip(f"Run: make {tooltip}")
        btn.setMinimumHeight(45)
        return btn
    
    def run_make(self, command: str):
        """Execute a make command"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already running. Please wait or stop it first.")
            return
        
        self.console.clear()
        self.statusBar().showMessage(f"Running: make {command}...")
        self.stop_btn.setEnabled(True)
        
        # Disable all buttons except stop
        for widget in self.centralWidget().findChildren(QPushButton):
            if widget != self.stop_btn:
                widget.setEnabled(False)
        
        self.worker = MakeWorker(command)
        self.worker.output.connect(self.append_output)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
    
    def stop_operation(self):
        """Stop the current operation"""
        if self.worker:
            self.worker.stop()
            self.console.append("\n⚠️  Stopping operation...\n")
    
    def append_output(self, text: str):
        """Append output to console"""
        self.console.insertPlainText(text)
        self.console.ensureCursorVisible()
    
    def on_finished(self, success: bool, message: str):
        """Handle operation completion"""
        self.console.append(f"\n{message}\n")
        self.statusBar().showMessage(message)
        self.stop_btn.setEnabled(False)
        
        # Re-enable all buttons
        for widget in self.centralWidget().findChildren(QPushButton):
            widget.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Failed", message)
    
    def clean_results(self):
        """Clean results with confirmation"""
        reply = QMessageBox.question(
            self,
            "Confirm Clean",
            "This will delete all simulation results, plots, and CSV exports.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.run_make("clean")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
<h2>Stelvio V2X Simulation Help</h2>

<h3>Workflow:</h3>
<ol>
<li><b>Build</b>: Compile the scenario (required first time)</li>
<li><b>Run Simulations</b>: Execute simulations with standard parameters
    <ul>
    <li>Crashed: Immediate DENM from crashed vehicle</li>
    <li>Witness: Delayed DENM from witness (3s delay standard)</li>
    </ul>
</li>
<li><b>Generate Plots</b>: Create visualization</li>
<li><b>Export CSV</b>: Export real simulation results to CSV format</li>
</ol>

<h3>Infrastructure Types:</h3>
<ul>
<li><b>Terrestrial</b>: 6G antenna (~5ms latency, 600m range)</li>
<li><b>Satellite</b>: LEO satellite (~45ms latency, 5000m range)</li>
<li><b>Hybrid</b>: Both terrestrial + satellite</li>
</ul>

<h3>Make Commands:</h3>
<ul>
<li><code>make build</code> - Build scenario</li>
<li><code>make run</code> - Run all scenarios</li>
<li><code>make analyze</code> - Generate plots</li>
<li><code>make export-csv</code> - Export to CSV</li>
<li><code>make clean</code> - Clean all results</li>
</ul>

<p><b>Note:</b> CSV exports contain real simulation data.</p>
"""
        QMessageBox.about(self, "Help", help_text)


# =============================================================================
# Main
# =============================================================================

def main():
    """Launch GUI"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = StelvioGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
