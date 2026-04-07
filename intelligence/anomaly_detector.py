"""
NOVA - Anomaly Detector
Detect unusual system behavior, security threats,
pattern breaks, and unexpected changes
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from collections import defaultdict

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AnomalyDetector:
    """
    Monitors for anomalies:
    1. Unusual system resource usage
    2. Unexpected process launches
    3. File system changes in critical directories
    4. Login/access pattern anomalies
    5. Network activity anomalies
    6. Unusual command patterns
    """

    def __init__(self, alert_callback: Callable = None):
        self.alert_callback = alert_callback
        self.running = False
        self.thread = None
        self.baselines = {}  # Normal behavior baselines
        self.anomalies_detected = []
        self.check_interval = 120  # 2 minutes
        self.known_processes = set()
        self._load_state()
        logger.info("Anomaly Detector initialized")

    def _state_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "anomaly_state.json")

    def _load_state(self):
        """Load baselines and state"""
        try:
            path = self._state_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.baselines = data.get("baselines", {})
                    self.known_processes = set(data.get("known_processes", []))
                    self.anomalies_detected = data.get("anomalies", [])[-100:]
        except Exception:
            pass

    def _save_state(self):
        """Save state"""
        try:
            os.makedirs(os.path.dirname(self._state_file()), exist_ok=True)
            with open(self._state_file(), 'w', encoding='utf-8') as f:
                json.dump({
                    "baselines": self.baselines,
                    "known_processes": list(self.known_processes)[:500],
                    "anomalies": self.anomalies_detected[-100:],
                    "last_save": datetime.now().isoformat()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save anomaly state: {e}")

    def update_baseline(self):
        """Update baseline measurements of normal behavior"""
        try:
            import psutil

            cpu_samples = []
            for _ in range(3):
                cpu_samples.append(psutil.cpu_percent(interval=1))

            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')

            # Get current processes
            current_procs = set()
            for proc in psutil.process_iter(['name']):
                try:
                    current_procs.add(proc.info['name'])
                except Exception:
                    pass

            now = datetime.now()
            hour_key = str(now.hour)

            if hour_key not in self.baselines:
                self.baselines[hour_key] = {
                    "cpu_samples": [],
                    "memory_samples": [],
                    "process_counts": [],
                }

            baseline = self.baselines[hour_key]
            baseline["cpu_samples"].append(sum(cpu_samples) / len(cpu_samples))
            baseline["memory_samples"].append(mem.percent)
            baseline["process_counts"].append(len(current_procs))

            # Keep only last 20 samples per hour
            for key in ["cpu_samples", "memory_samples", "process_counts"]:
                baseline[key] = baseline[key][-20:]

            # Update known processes
            self.known_processes.update(current_procs)

            self._save_state()

        except Exception as e:
            logger.error(f"Baseline update error: {e}")

    def check_anomalies(self) -> List[Dict]:
        """Run all anomaly checks"""
        anomalies = []

        try:
            import psutil

            # 1. CPU anomaly
            cpu_anomaly = self._check_cpu_anomaly()
            if cpu_anomaly:
                anomalies.append(cpu_anomaly)

            # 2. Memory anomaly
            mem_anomaly = self._check_memory_anomaly()
            if mem_anomaly:
                anomalies.append(mem_anomaly)

            # 3. New/unknown process detection
            proc_anomalies = self._check_process_anomalies()
            anomalies.extend(proc_anomalies)

            # 4. Disk space sudden change
            disk_anomaly = self._check_disk_anomaly()
            if disk_anomaly:
                anomalies.append(disk_anomaly)

            # 5. Network connection anomaly
            net_anomaly = self._check_network_anomaly()
            if net_anomaly:
                anomalies.append(net_anomaly)

        except Exception as e:
            logger.error(f"Anomaly check error: {e}")

        # Record anomalies
        for anomaly in anomalies:
            anomaly["timestamp"] = datetime.now().isoformat()
            self.anomalies_detected.append(anomaly)

        if anomalies:
            self._save_state()

        return anomalies

    def _check_cpu_anomaly(self) -> Optional[Dict]:
        """Check for CPU usage anomaly"""
        try:
            import psutil
            current_cpu = psutil.cpu_percent(interval=1)
            hour_key = str(datetime.now().hour)

            baseline = self.baselines.get(hour_key, {})
            cpu_samples = baseline.get("cpu_samples", [])

            if len(cpu_samples) >= 5:
                avg = sum(cpu_samples) / len(cpu_samples)
                std = (sum((x - avg) ** 2 for x in cpu_samples) / len(cpu_samples)) ** 0.5

                if current_cpu > avg + 2 * max(std, 10):  # 2 standard deviations
                    return {
                        "type": "cpu_anomaly",
                        "severity": "high" if current_cpu > 95 else "medium",
                        "message": f"Unusual CPU usage: {current_cpu}% (normal: {avg:.0f}% +/- {std:.0f}%)",
                        "value": current_cpu,
                        "expected": avg,
                    }
        except Exception:
            pass
        return None

    def _check_memory_anomaly(self) -> Optional[Dict]:
        """Check for memory usage anomaly"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            hour_key = str(datetime.now().hour)

            baseline = self.baselines.get(hour_key, {})
            mem_samples = baseline.get("memory_samples", [])

            if len(mem_samples) >= 5:
                avg = sum(mem_samples) / len(mem_samples)
                if mem.percent > avg + 20:  # 20% above normal
                    return {
                        "type": "memory_anomaly",
                        "severity": "high" if mem.percent > 95 else "medium",
                        "message": f"Unusual memory usage: {mem.percent}% (normal: {avg:.0f}%)",
                        "value": mem.percent,
                        "expected": avg,
                    }
        except Exception:
            pass
        return None

    def _check_process_anomalies(self) -> List[Dict]:
        """Check for new/unknown processes"""
        anomalies = []
        try:
            import psutil
            current_procs = set()
            for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
                try:
                    name = proc.info['name']
                    current_procs.add(name)

                    # Check for unknown processes (only after baseline is established)
                    if self.known_processes and name not in self.known_processes:
                        # Skip common system processes
                        skip_patterns = ["svchost", "runtime", "conhost", "dwm",
                                         "system", "idle", "csrss", "wininit"]
                        if not any(p in name.lower() for p in skip_patterns):
                            anomalies.append({
                                "type": "new_process",
                                "severity": "low",
                                "message": f"New process detected: {name} (PID: {proc.info['pid']})",
                                "process": name,
                            })

                    # Check for single process using excessive CPU
                    cpu = proc.info.get('cpu_percent', 0)
                    if cpu and cpu > 50:
                        anomalies.append({
                            "type": "high_cpu_process",
                            "severity": "medium",
                            "message": f"Process {name} using {cpu}% CPU",
                            "process": name,
                            "cpu": cpu,
                        })

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except Exception:
            pass
        return anomalies[:5]  # Limit to 5

    def _check_disk_anomaly(self) -> Optional[Dict]:
        """Check for disk space anomalies"""
        try:
            import psutil
            disk = psutil.disk_usage('C:')
            free_gb = disk.free / (1024**3)

            # Alert if less than 5GB free
            if free_gb < 5:
                return {
                    "type": "disk_critical",
                    "severity": "high",
                    "message": f"Critical disk space: only {free_gb:.1f}GB free on C:",
                    "value": free_gb,
                }
        except Exception:
            pass
        return None

    def _check_network_anomaly(self) -> Optional[Dict]:
        """Check for network anomalies"""
        try:
            import psutil
            connections = psutil.net_connections(kind='inet')
            established = [c for c in connections if c.status == 'ESTABLISHED']

            # Check for unusually many connections
            if len(established) > 100:
                return {
                    "type": "high_connections",
                    "severity": "medium",
                    "message": f"Unusually many network connections: {len(established)}",
                    "value": len(established),
                }
        except Exception:
            pass
        return None

    def check_command_anomaly(self, command: str, history: List[Dict]) -> Optional[Dict]:
        """Check if a command is anomalous based on history"""
        # Check for dangerous commands
        dangerous_patterns = [
            "rm -rf /", "del /s /q c:", "format c:",
            "shutdown", "restart", ":(){:|:&};:",  # fork bomb
            "dd if=", "mkfs",
        ]

        cmd_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in cmd_lower:
                return {
                    "type": "dangerous_command",
                    "severity": "critical",
                    "message": f"Potentially dangerous command detected: {command[:50]}",
                    "command": command,
                }

        # Check if command is unusual for current time
        now = datetime.now()
        hour = now.hour
        if history:
            hour_commands = [h for h in history if
                            h.get("timestamp", "").startswith(f"{now.strftime('%Y-%m-%d')}")]
            if len(hour_commands) > 50:  # Unusually many commands
                return {
                    "type": "high_activity",
                    "severity": "low",
                    "message": f"Unusually high command activity: {len(hour_commands)} commands today",
                }

        return None

    def start_background(self):
        """Start background anomaly detection"""
        if self.running:
            return

        self.running = True

        def _loop():
            # Initial baseline
            self.update_baseline()

            while self.running:
                try:
                    # Check for anomalies
                    anomalies = self.check_anomalies()
                    for anomaly in anomalies:
                        if anomaly["severity"] in ("high", "critical"):
                            if self.alert_callback:
                                self.alert_callback(anomaly["type"], anomaly["message"])

                    # Update baseline periodically
                    self.update_baseline()

                except Exception as e:
                    logger.error(f"Anomaly detector error: {e}")

                time.sleep(self.check_interval)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()
        logger.info("Anomaly detector started")

    def stop(self):
        """Stop background detection"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def get_anomaly_report(self) -> str:
        """Get anomaly report"""
        if not self.anomalies_detected:
            return "No anomalies detected. System is operating normally."

        report = "**Anomaly Report**\n\n"

        # Group by type
        by_type = defaultdict(list)
        for a in self.anomalies_detected[-50:]:
            by_type[a["type"]].append(a)

        for atype, items in by_type.items():
            severity = items[-1].get("severity", "unknown")
            report += f"**{atype}** (severity: {severity}) - {len(items)} occurrences\n"
            report += f"  Latest: {items[-1].get('message', 'N/A')}\n\n"

        return report
