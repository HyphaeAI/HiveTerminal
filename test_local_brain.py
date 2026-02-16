#!/usr/bin/env python3
"""Quick test script for Local Brain mode."""

import sys
sys.path.insert(0, '.')

from local_core.agent import run_local_agent

if __name__ == "__main__":
    print("Testing Local Brain Mode...")
    print("=" * 50)
    run_local_agent()
