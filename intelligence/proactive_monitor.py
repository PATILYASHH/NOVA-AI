"""
NOVA - Proactive Monitoring System
Watches system, sends morning briefings, alerts before problems happen
"""

import os
import json
import psutil
import logging
import threading
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONITOR_DATA = os.path.join(BASE_DIR, "intelligence", "data", "monitor.json")


class ProactiveMonitor:
    """
    Monitors system health and alerts proactively
    """

    def __init__(self, alert_callback: Callable[[str, str], None] = None,
                 self_coder=None, reflection=None):
        self.alert_callback = alert_callback  # Function to send alerts
        self.self_coder = self_coder  # SelfCoder instance for 6PM review
        self.reflection = reflection  # SelfReflectionSystem for diary
        self.running = False
        self.monitor_thread = None
        self.alerts_sent = {}  # Track alerts to avoid spam
        self.thresholds = {
            "cpu_percent": 95,
            "memory_percent": 92,
            "disk_percent": 95,
            "battery_low": 15,
            "battery_critical": 5
        }
        self.check_interval = 300  # 5 minutes between checks
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
        """Send alert only for important things, no spam"""
        # Cooldown: 30 min for normal, 10 min for critical
        alert_key = f"{alert_type}_{priority}"
        now = datetime.now()
        cooldown = 600 if priority == "critical" else 1800  # 10 min or 30 min

        if alert_key in self.alerts_sent:
            last_sent = self.alerts_sent[alert_key]
            if (now - last_sent).seconds < cooldown:
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
        """Check for processes using excessive resources (only alert for extreme cases)"""
        alerts = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                # Only alert if a single process uses >50% RAM (extreme)
                if proc.info['memory_percent'] and proc.info['memory_percent'] > 50:
                    alerts.append(f"{proc.info['name']}: {proc.info['memory_percent']:.1f}% RAM")
            except:
                pass

        if alerts:
            return {
                "type": "process_heavy",
                "message": f"Heavy processes: {', '.join(alerts[:3])}",
                "priority": "normal"
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
        """Background monitoring loop with morning briefing"""
        briefing_sent_today = False
        last_date = datetime.now().date()

        while self.running:
            try:
                now = datetime.now()

                # Reset daily flags at midnight
                if now.date() != last_date:
                    briefing_sent_today = False
                    last_date = now.date()

                # Morning briefing at 9:00 AM
                if not briefing_sent_today and now.hour == 9 and now.minute < 2:
                    self._send_morning_briefing()
                    briefing_sent_today = True

                # Evening summary at 6:00 PM
                if now.hour == 18 and now.minute < 2:
                    self._send_evening_summary()

                # Regular health checks
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

    def _send_morning_briefing(self):
        """Send a morning briefing to Yash"""
        try:
            status = self.get_status()
            now = datetime.now()
            day_name = now.strftime("%A")

            briefing = f"Good morning Yash! Here's your {day_name} briefing:\n\n"
            briefing += f"**System:**\n"
            briefing += f"  CPU: {status.get('cpu_percent', '?')}%\n"
            briefing += f"  RAM: {status.get('memory_percent', '?')}%\n"
            briefing += f"  Disk: {status.get('disk_percent', '?')}% used ({status.get('disk_free_gb', '?')}GB free)\n"

            if status.get("battery_percent") is not None:
                plug = "plugged in" if status.get("battery_plugged") else "on battery"
                briefing += f"  Battery: {status['battery_percent']}% ({plug})\n"

            # Check for issues
            issues = []
            if status.get("disk_percent", 0) > 80:
                issues.append(f"Disk is {status['disk_percent']}% full")
            if status.get("memory_percent", 0) > 80:
                issues.append(f"RAM usage is high at {status['memory_percent']}%")

            if issues:
                briefing += f"\n**Heads up:**\n"
                for issue in issues:
                    briefing += f"  - {issue}\n"

            briefing += f"\nI'm ready whenever you are. What are we working on today?"

            self.send_alert("Morning Briefing", briefing, "info")
            logger.info("Morning briefing sent")
        except Exception as e:
            logger.error(f"Morning briefing error: {e}")

    def _send_evening_summary(self):
        """Send evening summary + self-coding proposals"""
        try:
            status = self.get_status()
            summary = f"End of day check-in:\n\n"
            summary += f"System health: CPU {status.get('cpu_percent', '?')}%, RAM {status.get('memory_percent', '?')}%\n"
            summary += f"Disk: {status.get('disk_free_gb', '?')}GB free\n"

            self.send_alert("Evening Summary", summary, "info")
        except Exception as e:
            logger.error(f"Evening summary error: {e}")

        # Write human diary entry for the day
        try:
            if self.reflection and hasattr(self.reflection, 'diary'):
                diary = self.reflection.diary
                perf = self.reflection.performance
                stats = {
                    "total_commands": perf.data.get("commands_executed", 0),
                    "successful": perf.data.get("commands_successful", 0),
                    "failed": perf.data.get("commands_failed", 0),
                    "errors": len(perf.data.get("errors_encountered", [])),
                }
                diary_entry = diary.write_human_diary(
                    nova_emotion="reflective",
                    yash_mood="neutral",
                    stats=stats
                )
                if diary_entry:
                    self.send_alert("Diary", "Wrote my diary for today.", "info")
                    logger.info("Daily diary entry written")
        except Exception as e:
            logger.error(f"Diary writing error: {e}")

        # Self-coding: analyze today's errors and propose fixes
        try:
            if self.self_coder:
                error_summary = self.self_coder.errors.get_today_summary()
                if error_summary["total"] > 0:
                    self.send_alert("Self-Review",
                        f"I encountered {error_summary['total']} errors today. "
                        f"Let me analyze and propose fixes...", "info")

                    proposals = self.self_coder.generate_fix_proposals()
                    if proposals:
                        for proposal in proposals:
                            msg = self.self_coder.format_proposal_message(proposal)
                            msg += f"\n\nReply `/fixapprove {proposal['id']}` to approve"
                            msg += f"\nReply `/fixreject {proposal['id']}` to reject"
                            self.send_alert("Fix Proposal", msg, "normal")
                    else:
                        self.send_alert("Self-Review",
                            "Analyzed today's errors but no code fixes needed. "
                            "The issues were external (network, user input, etc).", "info")
                else:
                    self.send_alert("Self-Review",
                        "Clean day! No errors encountered. Everything ran smoothly.", "info")
        except Exception as e:
            logger.error(f"Self-coding review error: {e}")

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
