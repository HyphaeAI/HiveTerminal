#!/usr/bin/env python3
"""Test script to verify StateTool is discoverable by Vibe's ToolManager."""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "Vibe"))

from vibe.core.paths.config_paths import unlock_config_paths
from vibe.core.config import VibeConfig
from vibe.core.tools.manager import ToolManager

def test_tool_discovery():
    """Test that StateTool is discovered by ToolManager."""
    print("=" * 60)
    print("Testing Tool Discovery")
    print("=" * 60)
    print()
    
    # Unlock config paths
    print("Unlocking config paths...")
    unlock_config_paths()
    print("  ✓ Config paths unlocked")
    print()
    
    # Load config
    print("Loading config...")
    config = VibeConfig()
    print(f"  ✓ Config loaded")
    print(f"  ✓ Tool paths: {config.tool_paths}")
    print()
    
    # Create tool manager
    print("Creating ToolManager...")
    tool_manager = ToolManager(lambda: config)
    print(f"  ✓ ToolManager created")
    print()
    
    # List available tools
    print("Available tools:")
    available = tool_manager.available_tools
    for name in sorted(available.keys()):
        print(f"  - {name}")
    print()
    
    # Check for state tool
    print("Checking for state tool...")
    if "state" in available:
        print("  ✓ StateTool found!")
        state_tool_class = available["state"]
        print(f"  ✓ Tool class: {state_tool_class.__name__}")
        print(f"  ✓ Description: {state_tool_class.description}")
        print()
        
        # Try to instantiate it
        print("Instantiating StateTool...")
        try:
            state_tool = tool_manager.get("state")
            print(f"  ✓ Tool instantiated: {state_tool}")
            print(f"  ✓ Tool name: {state_tool.get_name()}")
            print()
            print("=" * 60)
            print("✅ TOOL DISCOVERY SUCCESSFUL!")
            print("=" * 60)
            return True
        except Exception as e:
            print(f"  ✗ Failed to instantiate: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("  ✗ StateTool NOT found!")
        print()
        print("Available tools:")
        for name in sorted(available.keys()):
            print(f"  - {name}")
        print()
        print("=" * 60)
        print("❌ TOOL DISCOVERY FAILED!")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_tool_discovery()
    sys.exit(0 if success else 1)
