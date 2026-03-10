#!/usr/bin/env python3
"""
Agent Manager for handling A2A agent lifecycle within the backend service.

This module manages the startup and cleanup of all agents required for the
Agent-to-Agent (A2A) protocol communication, ensuring they are running
when the backend service starts.
"""

import asyncio
import logging
import os
import signal
import subprocess
import sys
import atexit
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class AgentsManager:
    """Manages the lifecycle of A2A agents as background processes."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.log_dir = Path(".logs")
        self.agents_dir = Path(__file__).parent / "agents"
        
        # Setup cleanup on exit
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)
    
    def setup_log_directory(self):
        """Create log directory for agent outputs."""
        self.log_dir.mkdir(exist_ok=True)
        # Clear old logs
        for log_file in self.log_dir.glob("*.log"):
            log_file.unlink()
        logger.info(f"Log directory setup at {self.log_dir}")
    
    def start_agent(self, agent_module: str, port: int, log_file: str) -> Optional[subprocess.Popen]:
        """Start a single agent as a background process."""
        try:
            # Build command similar to card flow run.sh
            cmd = ["uv", "run", "--no-sync", "--package", "backend-service"]
            
            # Add env file if it exists (like in card flow)
            env_file = Path.cwd().parent / ".env"
            if env_file.exists():
                cmd.extend(["--env-file", str(env_file)])
            
            # Add python module execution
            cmd.extend(["python", "-m", f"agents.roles.{agent_module}"])
            
            logger.info(f"Starting {agent_module} with command: {' '.join(cmd)}")
            
            log_path = self.log_dir / log_file
            
            with open(log_path, "w") as log_handle:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    cwd=Path.cwd(),
                    env=os.environ.copy()
                )
            
            self.processes.append(process)
            logger.info(f"Started {agent_module} on port {port} (PID: {process.pid}, log: {log_file})")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start {agent_module}: {e}")
            return None
    
    def start_all_agents(self):
        """Start all required agents for A2A communication."""
        logger.info("Starting all A2A agents...")
        
        # First, ensure the backend package is installed in editable mode
        self._ensure_package_installed()
        
        self.setup_log_directory()
        
        agents_config = [
            ("merchant_agent", 8001, "merchant_agent.log"),
            ("credentials_provider_agent", 8002, "credentials_provider_agent.log"),
            ("merchant_payment_processor_agent", 8003, "mpp_agent.log"),
            ("auditor_agent", 8004, "auditor_agent.log"),
        ]
        
        # Start A2A agents
        for agent_module, port, log_file in agents_config:
            self.start_agent(agent_module, port, log_file)
        
        # Give agents time to start up
        import time
        time.sleep(3)
        
        # Check if all processes are running
        running_count = sum(1 for p in self.processes if p.poll() is None)
        logger.info(f"Started {running_count}/{len(agents_config)} agents successfully")
        
        if running_count < len(agents_config):
            logger.warning("Not all agents started successfully. Check logs for details.")
    
    def _ensure_package_installed(self):
        """Ensure the backend package is installed in editable mode for proper imports."""
        try:
            logger.info("Ensuring backend package is installed in editable mode...")
            result = subprocess.run(
                ["uv", "pip", "install", "-e", "."],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.error(f"Failed to install package in editable mode: {result.stderr}")
            else:
                logger.info("Backend package installation verified")
        except Exception as e:
            logger.error(f"Error installing package: {e}")
    
    def cleanup(self):
        """Clean up all started agent processes."""
        if not self.processes:
            return
        
        logger.info("Shutting down A2A agents...")
        
        for process in self.processes:
            if process.poll() is None:  # Process is still running
                try:
                    process.terminate()
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't terminate gracefully
                        process.kill()
                        process.wait()
                    logger.info(f"Stopped agent process {process.pid}")
                except Exception as e:
                    logger.error(f"Error stopping process {process.pid}: {e}")
        
        self.processes.clear()
        logger.info("Agent cleanup complete")
    
    def is_healthy(self) -> bool:
        """Check if all agents are running properly."""
        if not self.processes:
            return False
        
        running_count = sum(1 for p in self.processes if p.poll() is None)
        return running_count == len(self.processes)
    
    def get_status(self) -> dict:
        """Get status of all managed agents."""
        status = {
            "total_agents": len(self.processes),
            "running_agents": sum(1 for p in self.processes if p.poll() is None),
            "agents": []
        }
        
        agents_info = [
            ("merchant_agent", 8001),
            ("credentials_provider_agent", 8002), 
            ("merchant_payment_processor_agent", 8003),
            ("auditor_agent", 8004),
        ]
        
        for i, (agent_name, port) in enumerate(agents_info):
            if i < len(self.processes):
                process = self.processes[i]
                status["agents"].append({
                    "name": agent_name,
                    "port": port,
                    "pid": process.pid,
                    "running": process.poll() is None
                })
        
        return status


# Global instance
agents_manager = AgentsManager()