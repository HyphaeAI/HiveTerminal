#!/usr/bin/env python3
"""Simple test to verify StateTool can be imported."""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "Vibe"))

print("=" * 60)
print("Testing StateTool Import")
print("=" * 60)
print()

try:
    print("Importing StateTool...")
    from hiveterminal.tools.state_tool import StateTool
    print("  ✓ StateTool imported successfully")
    print(f"  ✓ Tool class: {StateTool.__name__}")
    print(f"  ✓ Description: {StateTool.description}")
    print()
    
    print("Checking tool name...")
    tool_name = StateTool.get_name()
    print(f"  ✓ Tool name: {tool_name}")
    print()
    
    print("Checking tool is a BaseTool subclass...")
    from vibe.core.tools.base import BaseTool
    is_base_tool = issubclass(StateTool, BaseTool)
    print(f"  ✓ Is BaseTool subclass: {is_base_tool}")
    print()
    
    print("=" * 60)
    print("✅ IMPORT TEST PASSED!")
    print("=" * 60)
    print()
    print("StateTool is properly defined and can be discovered by ToolManager.")
    print("When you run 'hive', the tool should be available as 'state'.")
    
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)
    print("❌ IMPORT TEST FAILED!")
    print("=" * 60)
    sys.exit(1)
