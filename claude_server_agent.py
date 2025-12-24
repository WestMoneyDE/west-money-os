#!/usr/bin/env python3
"""
🔥 WEST MONEY OS - CLAUDE AI SERVER AGENT 🔥
Autonomer AI-Agent für Server-Überwachung und Management

Features:
- Datei-Überwachung
- Code-Analyse
- Security Scanning
- Performance Monitoring
- Auto-Healing
- Log-Analyse
"""

import os
import sys
import time
import json
import logging
import hashlib
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import requests
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server_agent.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('ClaudeServerAgent')


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AgentConfig:
    """Agent Configuration"""
    # Anthropic
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    claude_model: str = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    
    # Monitoring
    watch_directories: List[str] = field(default_factory=lambda: [
        '/home/claude/westmoney_v9',
        '/var/www/westmoney'
    ])
    check_interval: int = 60  # Sekunden
    
    # Alerts
    slack_webhook: str = os.getenv('SLACK_WEBHOOK', '')
    discord_webhook: str = os.getenv('DISCORD_WEBHOOK', '')
    alert_email: str = os.getenv('ALERT_EMAIL', '')
    
    # Thresholds
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0
    
    # Security
    security_scan_interval: int = 3600  # 1 Stunde
    
    # Auto-Healing
    auto_heal_enabled: bool = True
    max_auto_heal_attempts: int = 3


# =============================================================================
# CLAUDE AI SERVICE
# =============================================================================

class ClaudeAgentAI:
    """Claude AI für Server-Analyse und Entscheidungen"""
    
    API_URL = "https://api.anthropic.com/v1/messages"
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.conversation_history = []
    
    def _headers(self):
        return {
            'x-api-key': self.config.anthropic_api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
    
    def analyze(self, context: str, question: str) -> str:
        """Analysiert Situation und gibt Empfehlung"""
        
        system_prompt = """Du bist ein erfahrener DevOps-Ingenieur und Server-Administrator.
        
DEINE AUFGABEN:
- Analysiere Server-Metriken und Logs
- Erkenne Probleme und Sicherheitsrisiken
- Gib präzise Handlungsempfehlungen
- Erstelle Bash/Python-Befehle zur Problembehebung

AUSGABEFORMAT:
- Status: [OK|WARNING|CRITICAL]
- Analyse: [Kurze Analyse]
- Empfehlung: [Konkrete Maßnahmen]
- Befehle: [Falls nötig, ausführbare Befehle]

Sei präzise und technisch korrekt. Antworte auf Deutsch."""

        messages = [
            {
                'role': 'user',
                'content': f"KONTEXT:\n{context}\n\nFRAGE:\n{question}"
            }
        ]
        
        try:
            response = requests.post(
                self.API_URL,
                headers=self._headers(),
                json={
                    'model': self.config.claude_model,
                    'max_tokens': 2000,
                    'system': system_prompt,
                    'messages': messages
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                logger.error(f"Claude API Error: {response.status_code}")
                return f"Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Claude API Exception: {e}")
            return f"Exception: {e}"
    
    def generate_fix(self, problem_description: str) -> Optional[str]:
        """Generiert einen Fix-Befehl für ein Problem"""
        
        prompt = f"""Generiere einen Bash- oder Python-Befehl zur Behebung dieses Problems:

PROBLEM:
{problem_description}

Antworte NUR mit dem ausführbaren Befehl, keine Erklärung.
Wenn kein sicherer automatischer Fix möglich ist, antworte mit "MANUAL_REQUIRED"."""

        response = self.analyze("", prompt)
        
        if "MANUAL_REQUIRED" in response:
            return None
        
        return response.strip()


# =============================================================================
# FILE WATCHER
# =============================================================================

class FileWatcher:
    """Überwacht Dateiänderungen"""
    
    def __init__(self, directories: List[str]):
        self.directories = directories
        self.file_hashes: Dict[str, str] = {}
        self.changes: List[Dict] = []
    
    def _hash_file(self, filepath: str) -> str:
        """Berechnet MD5-Hash einer Datei"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def scan(self) -> List[Dict]:
        """Scannt nach Dateiänderungen"""
        changes = []
        current_files = {}
        
        for directory in self.directories:
            if not os.path.exists(directory):
                continue
                
            for root, dirs, files in os.walk(directory):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in [
                    '__pycache__', 'node_modules', '.git', 'venv', '.venv'
                ]]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    # Skip binary and large files
                    if file.endswith(('.pyc', '.pyo', '.so', '.db', '.sqlite')):
                        continue
                    
                    try:
                        stat = os.stat(filepath)
                        if stat.st_size > 10 * 1024 * 1024:  # 10MB
                            continue
                        
                        current_hash = self._hash_file(filepath)
                        current_files[filepath] = current_hash
                        
                        if filepath in self.file_hashes:
                            if self.file_hashes[filepath] != current_hash:
                                changes.append({
                                    'type': 'modified',
                                    'path': filepath,
                                    'time': datetime.now().isoformat()
                                })
                        else:
                            changes.append({
                                'type': 'created',
                                'path': filepath,
                                'time': datetime.now().isoformat()
                            })
                    except Exception:
                        continue
        
        # Check for deleted files
        for filepath in self.file_hashes:
            if filepath not in current_files:
                changes.append({
                    'type': 'deleted',
                    'path': filepath,
                    'time': datetime.now().isoformat()
                })
        
        self.file_hashes = current_files
        self.changes = changes
        
        return changes


# =============================================================================
# SECURITY SCANNER
# =============================================================================

class SecurityScanner:
    """Scannt Code auf Sicherheitsprobleme"""
    
    VULNERABILITY_PATTERNS = [
        # SQL Injection
        (r'execute\s*\(\s*["\'].*%s.*["\']', 'SQL Injection (String Format)'),
        (r'cursor\.execute\s*\(\s*f["\']', 'SQL Injection (f-string)'),
        
        # XSS
        (r'innerHTML\s*=', 'Potential XSS (innerHTML)'),
        (r'document\.write\s*\(', 'Potential XSS (document.write)'),
        
        # Command Injection
        (r'os\.system\s*\(', 'Command Injection (os.system)'),
        (r'subprocess\..*shell\s*=\s*True', 'Command Injection (shell=True)'),
        
        # Hardcoded Secrets
        (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded Password'),
        (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API Key'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded Secret'),
        
        # Insecure
        (r'verify\s*=\s*False', 'SSL Verification Disabled'),
        (r'DEBUG\s*=\s*True', 'Debug Mode Enabled'),
    ]
    
    def scan_file(self, filepath: str) -> List[Dict]:
        """Scannt eine einzelne Datei"""
        import re
        
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for pattern, issue_type in self.VULNERABILITY_PATTERNS:
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'file': filepath,
                                'line': i,
                                'type': issue_type,
                                'code': line.strip()[:100]
                            })
        except Exception as e:
            logger.error(f"Error scanning {filepath}: {e}")
        
        return issues
    
    def scan_directory(self, directory: str) -> List[Dict]:
        """Scannt ein Verzeichnis"""
        all_issues = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', 'node_modules', '.git', 'venv', '.venv'
            ]]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.php')):
                    filepath = os.path.join(root, file)
                    issues = self.scan_file(filepath)
                    all_issues.extend(issues)
        
        return all_issues


# =============================================================================
# PERFORMANCE MONITOR
# =============================================================================

class PerformanceMonitor:
    """Überwacht Server-Performance"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.history: List[Dict] = []
    
    def get_metrics(self) -> Dict:
        """Sammelt aktuelle Metriken"""
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Network
        network = psutil.net_io_counters()
        
        # Processes
        process_count = len(psutil.pids())
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            'processes': process_count
        }
        
        self.history.append(metrics)
        
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        return metrics
    
    def check_thresholds(self, metrics: Dict) -> List[Dict]:
        """Prüft auf Threshold-Überschreitungen"""
        alerts = []
        
        if metrics['cpu']['percent'] > self.config.cpu_threshold:
            alerts.append({
                'type': 'CPU',
                'level': 'WARNING' if metrics['cpu']['percent'] < 95 else 'CRITICAL',
                'value': metrics['cpu']['percent'],
                'threshold': self.config.cpu_threshold
            })
        
        if metrics['memory']['percent'] > self.config.memory_threshold:
            alerts.append({
                'type': 'MEMORY',
                'level': 'WARNING' if metrics['memory']['percent'] < 95 else 'CRITICAL',
                'value': metrics['memory']['percent'],
                'threshold': self.config.memory_threshold
            })
        
        if metrics['disk']['percent'] > self.config.disk_threshold:
            alerts.append({
                'type': 'DISK',
                'level': 'WARNING' if metrics['disk']['percent'] < 95 else 'CRITICAL',
                'value': metrics['disk']['percent'],
                'threshold': self.config.disk_threshold
            })
        
        return alerts


# =============================================================================
# LOG ANALYZER
# =============================================================================

class LogAnalyzer:
    """Analysiert Server-Logs"""
    
    ERROR_PATTERNS = [
        r'ERROR',
        r'CRITICAL',
        r'Exception',
        r'Traceback',
        r'FATAL',
        r'failed',
        r'denied',
        r'unauthorized',
        r'timeout',
    ]
    
    def __init__(self, log_files: List[str] = None):
        self.log_files = log_files or [
            '/home/claude/westmoney_v9/logs/flask.log',
            '/home/claude/westmoney_v9/logs/bots.log',
            '/home/claude/westmoney_v9/server_agent.log',
            '/var/log/nginx/error.log',
            '/var/log/syslog'
        ]
    
    def get_recent_errors(self, minutes: int = 30) -> List[Dict]:
        """Holt aktuelle Fehler aus Logs"""
        import re
        
        errors = []
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        for log_file in self.log_files:
            if not os.path.exists(log_file):
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read last 1000 lines
                    lines = f.readlines()[-1000:]
                    
                    for line in lines:
                        for pattern in self.ERROR_PATTERNS:
                            if re.search(pattern, line, re.IGNORECASE):
                                errors.append({
                                    'file': log_file,
                                    'line': line.strip()[:200],
                                    'pattern': pattern
                                })
                                break
            except Exception as e:
                logger.error(f"Error reading {log_file}: {e}")
        
        return errors


# =============================================================================
# ALERT MANAGER
# =============================================================================

class AlertManager:
    """Sendet Benachrichtigungen"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.sent_alerts: Dict[str, datetime] = {}
        self.cooldown_minutes = 15  # Keine doppelten Alerts
    
    def _should_send(self, alert_key: str) -> bool:
        """Prüft Cooldown"""
        if alert_key in self.sent_alerts:
            if datetime.now() - self.sent_alerts[alert_key] < timedelta(minutes=self.cooldown_minutes):
                return False
        return True
    
    def send_slack(self, message: str, level: str = 'info'):
        """Sendet Slack-Nachricht"""
        if not self.config.slack_webhook:
            return
        
        color = {
            'info': '#36a64f',
            'warning': '#ffcc00',
            'critical': '#ff0000'
        }.get(level, '#808080')
        
        payload = {
            'attachments': [{
                'color': color,
                'title': f'🤖 West Money Server Agent',
                'text': message,
                'ts': int(time.time())
            }]
        }
        
        try:
            requests.post(self.config.slack_webhook, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Slack alert failed: {e}")
    
    def send_discord(self, message: str, level: str = 'info'):
        """Sendet Discord-Nachricht"""
        if not self.config.discord_webhook:
            return
        
        color = {
            'info': 0x36a64f,
            'warning': 0xffcc00,
            'critical': 0xff0000
        }.get(level, 0x808080)
        
        payload = {
            'embeds': [{
                'title': '🤖 West Money Server Agent',
                'description': message,
                'color': color,
                'timestamp': datetime.utcnow().isoformat()
            }]
        }
        
        try:
            requests.post(self.config.discord_webhook, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Discord alert failed: {e}")
    
    def send_alert(self, title: str, message: str, level: str = 'info'):
        """Sendet Alert an alle konfigurierten Kanäle"""
        alert_key = f"{title}:{level}"
        
        if not self._should_send(alert_key):
            return
        
        full_message = f"**{title}**\n{message}"
        
        self.send_slack(full_message, level)
        self.send_discord(full_message, level)
        
        self.sent_alerts[alert_key] = datetime.now()
        logger.info(f"Alert sent: {title} [{level}]")


# =============================================================================
# AUTO HEALER
# =============================================================================

class AutoHealer:
    """Automatische Problembehebung"""
    
    def __init__(self, config: AgentConfig, ai: ClaudeAgentAI):
        self.config = config
        self.ai = ai
        self.heal_attempts: Dict[str, int] = {}
    
    def can_heal(self, issue_id: str) -> bool:
        """Prüft ob Auto-Heal möglich"""
        if not self.config.auto_heal_enabled:
            return False
        
        attempts = self.heal_attempts.get(issue_id, 0)
        return attempts < self.config.max_auto_heal_attempts
    
    def heal(self, issue_type: str, details: str) -> bool:
        """Versucht Problem automatisch zu beheben"""
        issue_id = f"{issue_type}:{details[:50]}"
        
        if not self.can_heal(issue_id):
            return False
        
        self.heal_attempts[issue_id] = self.heal_attempts.get(issue_id, 0) + 1
        
        # Vordefinierte Fixes
        fixes = {
            'high_memory': 'sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true',
            'high_disk': 'find /tmp -type f -mtime +7 -delete 2>/dev/null || true',
            'process_restart': 'systemctl restart westmoney 2>/dev/null || supervisorctl restart westmoney 2>/dev/null || true'
        }
        
        if issue_type in fixes:
            try:
                subprocess.run(fixes[issue_type], shell=True, timeout=30)
                logger.info(f"Auto-heal executed: {issue_type}")
                return True
            except Exception as e:
                logger.error(f"Auto-heal failed: {e}")
                return False
        
        # AI-generierter Fix
        fix_command = self.ai.generate_fix(details)
        
        if fix_command:
            logger.info(f"AI-generated fix: {fix_command}")
            # ACHTUNG: In Produktion sollte hier eine Bestätigung erfolgen!
            # subprocess.run(fix_command, shell=True, timeout=30)
            return True
        
        return False


# =============================================================================
# MAIN AGENT
# =============================================================================

class ClaudeServerAgent:
    """Hauptklasse des Server-Agents"""
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.ai = ClaudeAgentAI(self.config)
        self.file_watcher = FileWatcher(self.config.watch_directories)
        self.security_scanner = SecurityScanner()
        self.performance_monitor = PerformanceMonitor(self.config)
        self.log_analyzer = LogAnalyzer()
        self.alert_manager = AlertManager(self.config)
        self.auto_healer = AutoHealer(self.config, self.ai)
        
        self.running = False
        self.last_security_scan = None
    
    def run_check(self):
        """Führt einen kompletten Check durch"""
        logger.info("🔍 Starting system check...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'performance': {},
            'file_changes': [],
            'security_issues': [],
            'log_errors': [],
            'alerts': []
        }
        
        # 1. Performance Check
        metrics = self.performance_monitor.get_metrics()
        results['performance'] = metrics
        
        alerts = self.performance_monitor.check_thresholds(metrics)
        for alert in alerts:
            results['alerts'].append(alert)
            self.alert_manager.send_alert(
                f"{alert['type']} Alert",
                f"Wert: {alert['value']:.1f}% (Threshold: {alert['threshold']}%)",
                'warning' if alert['level'] == 'WARNING' else 'critical'
            )
            
            # Auto-Heal versuchen
            if alert['type'] == 'MEMORY' and alert['level'] == 'CRITICAL':
                self.auto_healer.heal('high_memory', str(alert))
        
        # 2. File Changes
        changes = self.file_watcher.scan()
        results['file_changes'] = changes
        
        if changes:
            logger.info(f"📁 {len(changes)} file changes detected")
            
            # Bei kritischen Dateien warnen
            for change in changes:
                if any(x in change['path'] for x in ['.env', 'config', 'settings']):
                    self.alert_manager.send_alert(
                        "Konfigurationsänderung",
                        f"{change['type']}: {change['path']}",
                        'warning'
                    )
        
        # 3. Security Scan (periodisch)
        if (self.last_security_scan is None or 
            (datetime.now() - self.last_security_scan).seconds > self.config.security_scan_interval):
            
            logger.info("🔒 Running security scan...")
            
            for directory in self.config.watch_directories:
                if os.path.exists(directory):
                    issues = self.security_scanner.scan_directory(directory)
                    results['security_issues'].extend(issues)
            
            if results['security_issues']:
                self.alert_manager.send_alert(
                    "Sicherheitsprobleme gefunden",
                    f"{len(results['security_issues'])} potentielle Sicherheitslücken",
                    'critical'
                )
            
            self.last_security_scan = datetime.now()
        
        # 4. Log Analysis
        errors = self.log_analyzer.get_recent_errors(30)
        results['log_errors'] = errors[:20]  # Max 20 Fehler
        
        if len(errors) > 10:
            self.alert_manager.send_alert(
                "Viele Log-Fehler",
                f"{len(errors)} Fehler in den letzten 30 Minuten",
                'warning'
            )
        
        # 5. AI-Analyse bei kritischen Problemen
        if results['alerts'] or len(results['security_issues']) > 5:
            context = json.dumps(results, indent=2, default=str)[:3000]
            analysis = self.ai.analyze(context, "Analysiere diese Server-Situation und gib Empfehlungen.")
            results['ai_analysis'] = analysis
            logger.info(f"🤖 AI Analysis:\n{analysis}")
        
        logger.info(f"✅ System check complete: {len(results['alerts'])} alerts")
        
        return results
    
    def start(self):
        """Startet den Agent"""
        self.running = True
        
        logger.info("""
╔═══════════════════════════════════════════════════════════════╗
║  🤖 CLAUDE SERVER AGENT - ACTIVE                              ║
║  BROLY ULTRA GODMODE - Autonomous Server Monitoring           ║
╠═══════════════════════════════════════════════════════════════╣
║  Watching: {dirs}
║  Interval: {interval}s
║  Auto-Heal: {heal}
╚═══════════════════════════════════════════════════════════════╝
        """.format(
            dirs=len(self.config.watch_directories),
            interval=self.config.check_interval,
            heal='ENABLED' if self.config.auto_heal_enabled else 'DISABLED'
        ))
        
        # Initial scan
        self.file_watcher.scan()
        
        while self.running:
            try:
                self.run_check()
            except Exception as e:
                logger.error(f"Check failed: {e}")
                self.alert_manager.send_alert(
                    "Agent Error",
                    str(e),
                    'critical'
                )
            
            time.sleep(self.config.check_interval)
    
    def stop(self):
        """Stoppt den Agent"""
        self.running = False
        logger.info("🛑 Claude Server Agent stopped")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main Entry Point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Server Agent')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--watch', nargs='+', help='Directories to watch')
    args = parser.parse_args()
    
    config = AgentConfig()
    
    if args.interval:
        config.check_interval = args.interval
    
    if args.watch:
        config.watch_directories = args.watch
    
    agent = ClaudeServerAgent(config)
    
    if args.once:
        results = agent.run_check()
        print(json.dumps(results, indent=2, default=str))
    else:
        try:
            agent.start()
        except KeyboardInterrupt:
            agent.stop()


if __name__ == '__main__':
    main()
