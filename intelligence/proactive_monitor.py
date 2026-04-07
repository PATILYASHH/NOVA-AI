"""
NOVA - Proactive Monitoring System
Watches system and alerts before problems happen
"""

import os
import json
import psutil
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONITOR_DATA = os.path.join(BASE_DIR, "intelligence", "data", "monitor.json")


class ProactiveMonitor:
    """
    Monitors system health and alerts proactively
    """

    def __init__(self, alert_callback: Callable[[str, str], None] = None):
        self.alert_callback = alert_callback  # Function to send alerts
        self.running = False
        self.monitor_thread = None
        self.alerts_sent = {}  # Track alerts to avoid spam
        self.thresholds = {
            "cpu_percent": 90,
            "memory_percent": 85,
            "disk_percent": 90,
            "battery_low": 20,
            "battery_critical": 10
        }
        self.check_interval = 60  # seconds
        self.load_state()

    def load_state(self):
        """Load monitor state"""
        try:
            if os.path.exists(MONITOR_DATA):
                with open(MONITOR_DATA, 'r') as f:
                    data = json.load(f)
                    self.thresholds.update(data.get("thresholds", {}))
        except:
            pass

    def save_state(self):
        """Save monitor state"""
        try:
            os.makedirs(os.path.dirname(MONITOR_DATA), exist_ok=True)
            with open(MONITOR_DATA, 'w') as f:
                json.dump({
                    "thresholds": self.thresholds,
                    "last_check": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save monitor state: {e}")

    def set_threshold(self, metric: str, value: int):
        """Set alert threshold"""
        self.thresholds[metric] = value
        self.save_state()

    def send_alert(self, alert_type: str, message: str, priority: str = "normal"):
        """Send alert if not recently sent"""
        # Avoid duplicate alerts within 5 minutes
        alert_key = f"{alert_type}_{priority}"
        now = datetime.now()

        if alert_key in self.alerts_sent:
            last_sent = self.alerts_sent[alert_key]
            if (now - last_sent).seconds < 300:  # 5 minutes
                return

        self.alerts_sent[alert_key] = now

        if self.alert_callback:
            self.alert_callback(alert_type, message)
        else:
            logger.warning(f"ALERT [{priority}] {alert_type}: {message}")

    def check_cpu(self) -> Optional[Dict]:
        """Check CPU usage"""
        cpu = psutil.cpu_percent(interval=1)
        if cpu > self.thresholds["cpu_percent"]:
            return {
                "type": "cpu_high",
                "value": cpu,
                "threshold": self.thresholds["cpu_percent"],
                "message": f"CPU usage is high: {cpu}%",
                "priority": "high" if cpu > 95 else "normal"
            }
        return None

    def check_memory(self) -> Optional[Dict]:
        """Check memory usage"""
        mem = psutil.virtual_memory()
        if mem.percent > self.thresholds["memory_percent"]:
            return {
                "type": "memory_high",
                "value": mem.percent,
                "threshold": self.thresholds["memory_percent"],
                "message": f"Memory usage is high: {mem.percent}% ({mem.used // (1024**3)}GB used)",
                "priority": "high" if mem.percent > 95 else "normal"
            }
        return None

    def check_disk(self) -> Optional[Dict]:
        """Check disk usage"""
        try:
            disk = psutil.disk_usage('C:')
            if disk.percent > self.thresholds["disk_percent"]:
                free_gb = disk.free // (1024**3)
                return {
                    "type": "disk_low",
                    "value": disk.percent,
                    "threshold": self.thresholds["disk_percent"],
                    "message": f"Disk space low: {disk.percent}% used, {free_gb}GB free",
                    "priority": "high" if free_gb < 5 else "normal"
                }
        except:
            pass
        return None

    def check_battery(self) -> Optional[Dict]:
        """Check battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery and not battery.power_plugged:
                if battery.percent <= self.thresholds["battery_critical"]:
                    return {
                        "type": "battery_critical",
                        "value": battery.percent,
                        "message": f"CRITICAL: Battery at {battery.percent}%! Plug in now!",
                        "priority": "critical"
                    }
                elif battery.percent <= self.thresholds["battery_low"]:
                    return {
                        "type": "battery_low",
                        "value": battery.percent,
                        "message": f"Battery low: {battery.percent}%",
                        "priority": "normal"
                    }
        except:
            pass
        return None

    def check_large_processes(self) -> Optional[Dict]:
        """Check for processes using too much resources"""
        alerts = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['memory_percent'] and proc.info['memory_percent'] > 30:
                    alerts.append(f"{proc.info['name']}: {proc.info['memory_percent']:.1f}% RAM")
            except:
                pass

        if alerts:
            return {
                "type": "process_heavy",
                "message": f"Heavy processes: {', '.join(alerts[:3])}",
                "priority": "low"
            }
        return None

    def check_all(self) -> List[Dict]:
        """Run all checks"""
        alerts = []

        checks = [
            self.check_cpu,
            self.check_memory,
            self.check_disk,
            self.check_battery,
            self.check_large_processes
        ]

        for check in checks:
            try:
                result = check()
                if result:
                    alerts.append(result)
            except Exception as e:
                logger.error(f"Check failed: {e}")

        return alerts

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                alerts = self.check_all()
                for alert in alerts:
                    self.send_alert(
                        alert["type"],
                        alert["message"],
                        alert.get("priority", "normal")
                    )
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

            time.sleep(self.check_interval)

    def start(self):
        """Start background monitoring"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Proactive monitor started")

    def stop(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Proactive monitor stopped")

    def get_status(self) -> Dict:
        """Get current system status"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')

            status = {
                "cpu_percent": cpu,
                "memory_percent": mem.percent,
                "memory_used_gb": mem.used // (1024**3),
                "memory_total_gb": mem.total // (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free // (1024**3),
                "thresholds": self.thresholds,
                "monitoring_active": self.running
            }

            try:
                battery = psutil.sensors_battery()
                if battery:
                    status["battery_percent"] = battery.percent
                    status["battery_plugged"] = battery.power_plugged
            except:
                pass

            return status
        except Exception as e:
            return {"error": str(e)}
