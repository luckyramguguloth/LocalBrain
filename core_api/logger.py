import logging
import os
import sys

# Configure logging path in the workspace root for simplicity
LOG_FILE = "app_runtime.log"

# Define log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s"

class ConsoleFormatter(logging.Formatter):
    """Custom formatter to add neon cyber colors for console output."""
    
    CYAN = "\033[96m"
    VIOLET = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    
    def format(self, record):
        log_fmt = LOG_FORMAT
        # Check if terminal supports colors
        if sys.platform != "win32" or os.environ.get("ANSICON") or os.environ.get("TERM") == "xterm":
            if record.levelno == logging.INFO:
                log_fmt = f"{self.CYAN}%(asctime)s{self.RESET} | {self.GREEN}%(levelname)-8s{self.RESET} | [{self.VIOLET}%(name)s{self.RESET}] %(message)s"
            elif record.levelno == logging.WARNING:
                log_fmt = f"{self.CYAN}%(asctime)s{self.RESET} | {self.YELLOW}%(levelname)-8s{self.RESET} | [{self.VIOLET}%(name)s{self.RESET}] %(message)s"
            elif record.levelno >= logging.ERROR:
                log_fmt = f"{self.CYAN}%(asctime)s{self.RESET} | {self.RED}%(levelname)-8s{self.RESET} | [{self.VIOLET}%(name)s{self.RESET}] %(message)s"
        
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

# Configure Root Logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Stream handler to Console (uses stderr so standard output remains clean for MCP JSON-RPC stdio streams)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(ConsoleFormatter())
root_logger.addHandler(console_handler)

# File handler to save logs persistently
try:
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(file_handler)
except Exception as ex:
    print(f"Warning: Could not configure file log handler: {ex}")

def get_logger(name: str) -> logging.Logger:
    """Returns a standard child logger by name."""
    return logging.getLogger(name)
