"""
Backend package initialization for the Lease Exit Workflow Management System.
This makes the backend directory a proper Python package.
"""

from .storage import Storage
from .agents import LeaseExitCrew

__all__ = [
    'Storage',
    'LeaseExitCrew'
]

"""
Flow.AI - Lease Exit Workflow Management System
"""

__version__ = "0.1.0"
