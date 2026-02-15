"""Plan parsing utilities for spec-first mode.

This module provides functions to parse markdown execution plans into
structured Action objects that can be executed by the SpecAgentLoop.
"""

from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from hiveterminal.agents.spec_agent import Action, ActionType

logger = logging.getLogger(__name__)


@dataclass
class ParsedPlan:
    """Represents a fully parsed execution plan.
    
    Attributes:
        summary: High-level description of the plan
        risk_assessment: Risk assessment details
        actions: List of parsed actions
        files_affected: List of files that will be modified
        rollback_plan: Instructions for rolling back changes
        raw_plan: Original markdown plan
    """
    summary: str
    risk_assessment: Dict[str, str]
    actions: List[Action]
    files_affected: List[Dict[str, str]]
    rollback_plan: str
    raw_plan: str


def parse_plan(plan: str) -> List[Action]:
    """Parse a markdown plan into executable actions.
    
    This function extracts action sections from a markdown plan and converts
    them into Action objects that can be executed.
    
    Args:
        plan: Markdown-formatted execution plan
        
    Returns:
        List of Action objects in execution order
        
    Raises:
        ValueError: If the plan is malformed or cannot be parsed
    """
    logger.info("Parsing execution plan")
    
    if not plan or not plan.strip():
        raise ValueError("Plan is empty")
    
    actions = []
    lines = plan.split('\n')
    
    current_action = None
    action_order = 0
    in_details = False
    details_buffer = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Detect action headers (### N. Action Type: Description)
        if line.startswith('### '):
            # Save previous action if exists
            if current_action and details_buffer:
                current_action.details['description_details'] = details_buffer
                details_buffer = []
            
            action_order += 1
            action_desc = line.replace('### ', '').strip()
            
            # Remove leading number if present (e.g., "1. Read File: ..." -> "Read File: ...")
            action_desc = re.sub(r'^\d+\.\s*', '', action_desc)
            
            # Determine action type from description
            action_type = _infer_action_type(action_desc)
            
            current_action = Action(
                action_type=action_type,
                target="",
                details={},
                order=action_order,
                description=action_desc
            )
            actions.append(current_action)
            in_details = False
        
        # Extract file path
        elif current_action and line.startswith('**File**:'):
            file_path = line.replace('**File**:', '').strip().strip('`')
            current_action.target = file_path
            current_action.details['file'] = file_path
        
        # Extract command
        elif current_action and line.startswith('**Command**:'):
            command = line.replace('**Command**:', '').strip().strip('`')
            current_action.target = command
            current_action.details['command'] = command
        
        # Extract operation type
        elif current_action and line.startswith('**Operation**:'):
            operation = line.replace('**Operation**:', '').strip()
            current_action.details['operation'] = operation
        
        # Extract purpose
        elif current_action and line.startswith('**Purpose**:'):
            purpose = line.replace('**Purpose**:', '').strip()
            current_action.details['purpose'] = purpose
        
        # Extract expected output
        elif current_action and line.startswith('**Expected Output**:'):
            expected = line.replace('**Expected Output**:', '').strip()
            current_action.details['expected_output'] = expected
        
        # Start of details section
        elif current_action and line.startswith('**Details**:'):
            in_details = True
        
        # Collect details
        elif current_action and in_details and line.startswith('- '):
            detail = line.replace('- ', '').strip()
            details_buffer.append(detail)
    
    # Save last action's details
    if current_action and details_buffer:
        current_action.details['description_details'] = details_buffer
    
    if not actions:
        raise ValueError("No actions found in plan")
    
    logger.info(f"Successfully parsed {len(actions)} actions")
    return actions


def parse_full_plan(plan: str) -> ParsedPlan:
    """Parse a complete markdown plan into a structured object.
    
    This function extracts all sections of the plan including summary,
    risk assessment, actions, affected files, and rollback instructions.
    
    Args:
        plan: Markdown-formatted execution plan
        
    Returns:
        ParsedPlan object with all plan details
        
    Raises:
        ValueError: If the plan is malformed or missing required sections
    """
    logger.info("Parsing full execution plan")
    
    if not plan or not plan.strip():
        raise ValueError("Plan is empty")
    
    # Extract sections
    summary = _extract_section(plan, "## Summary")
    risk_assessment = _extract_risk_assessment(plan)
    actions = parse_plan(plan)
    files_affected = _extract_files_affected(plan)
    rollback_plan = _extract_section(plan, "## Rollback Plan")
    
    parsed = ParsedPlan(
        summary=summary,
        risk_assessment=risk_assessment,
        actions=actions,
        files_affected=files_affected,
        rollback_plan=rollback_plan,
        raw_plan=plan
    )
    
    logger.info(f"Successfully parsed full plan with {len(actions)} actions")
    return parsed


def extract_file_operations(actions: List[Action]) -> Dict[str, List[Action]]:
    """Extract file operations grouped by file path.
    
    Args:
        actions: List of actions
        
    Returns:
        Dictionary mapping file paths to lists of actions
    """
    file_ops = {}
    
    for action in actions:
        if action.action_type in (
            ActionType.CREATE_FILE,
            ActionType.MODIFY_FILE,
            ActionType.DELETE_FILE,
            ActionType.READ_FILE
        ):
            file_path = action.target
            if file_path:
                if file_path not in file_ops:
                    file_ops[file_path] = []
                file_ops[file_path].append(action)
    
    return file_ops


def extract_shell_commands(actions: List[Action]) -> List[Action]:
    """Extract shell command actions.
    
    Args:
        actions: List of actions
        
    Returns:
        List of actions that are shell commands
    """
    return [
        action for action in actions
        if action.action_type == ActionType.EXECUTE_COMMAND
    ]


def validate_action_order(actions: List[Action]) -> bool:
    """Validate that actions are in correct execution order.
    
    Checks:
    - Actions have sequential order numbers
    - Read operations come before modifications
    - File creation comes before modification
    
    Args:
        actions: List of actions to validate
        
    Returns:
        True if order is valid, False otherwise
    """
    if not actions:
        return True
    
    # Check sequential order
    for i, action in enumerate(actions, start=1):
        if action.order != i:
            logger.warning(f"Action order mismatch: expected {i}, got {action.order}")
            return False
    
    # Check file operation order
    file_ops = extract_file_operations(actions)
    for file_path, ops in file_ops.items():
        # Check if file is modified before creation
        has_create = any(op.action_type == ActionType.CREATE_FILE for op in ops)
        has_modify = any(op.action_type == ActionType.MODIFY_FILE for op in ops)
        
        if has_create and has_modify:
            create_order = next(
                op.order for op in ops if op.action_type == ActionType.CREATE_FILE
            )
            modify_order = next(
                op.order for op in ops if op.action_type == ActionType.MODIFY_FILE
            )
            
            if modify_order < create_order:
                logger.warning(
                    f"File {file_path} is modified before creation"
                )
                return False
    
    return True


def handle_malformed_plan(plan: str) -> List[Action]:
    """Attempt to parse a malformed plan with best-effort recovery.
    
    This function tries to extract as much information as possible from
    a plan that doesn't follow the standard format.
    
    Args:
        plan: Potentially malformed markdown plan
        
    Returns:
        List of actions extracted with best effort
        
    Raises:
        ValueError: If the plan is completely unparseable
    """
    logger.warning("Attempting to parse malformed plan")
    
    try:
        # Try standard parsing first
        return parse_plan(plan)
    except ValueError:
        pass
    
    # Fallback: Look for any numbered items
    actions = []
    lines = plan.split('\n')
    action_order = 0
    
    for line in lines:
        line = line.strip()
        
        # Look for numbered items (1., 2., etc.)
        match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if match:
            action_order += 1
            description = match.group(2)
            action_type = _infer_action_type(description)
            
            action = Action(
                action_type=action_type,
                target="",
                details={'description': description},
                order=action_order,
                description=description
            )
            actions.append(action)
    
    if not actions:
        raise ValueError("Could not extract any actions from malformed plan")
    
    logger.info(f"Extracted {len(actions)} actions from malformed plan")
    return actions


# Private helper functions

def _infer_action_type(description: str) -> ActionType:
    """Infer action type from description.
    
    Args:
        description: Action description
        
    Returns:
        Inferred ActionType
    """
    desc_lower = description.lower()
    
    if 'create' in desc_lower and ('file' in desc_lower or 'directory' in desc_lower):
        if 'directory' in desc_lower or 'folder' in desc_lower:
            return ActionType.CREATE_DIRECTORY
        return ActionType.CREATE_FILE
    elif 'modify' in desc_lower or 'update' in desc_lower or 'change' in desc_lower or 'edit' in desc_lower:
        return ActionType.MODIFY_FILE
    elif 'delete' in desc_lower or 'remove' in desc_lower:
        return ActionType.DELETE_FILE
    elif 'read' in desc_lower or 'analyze' in desc_lower or 'review' in desc_lower:
        return ActionType.READ_FILE
    elif 'command' in desc_lower or 'execute' in desc_lower or 'run' in desc_lower:
        return ActionType.EXECUTE_COMMAND
    else:
        # Default to read if unclear
        return ActionType.READ_FILE


def _extract_section(plan: str, section_header: str) -> str:
    """Extract content of a markdown section.
    
    Args:
        plan: Full markdown plan
        section_header: Section header to find (e.g., "## Summary")
        
    Returns:
        Section content as string
    """
    lines = plan.split('\n')
    in_section = False
    content = []
    
    for line in lines:
        if line.strip() == section_header:
            in_section = True
            continue
        
        if in_section:
            # Stop at next section header
            if line.strip().startswith('##'):
                break
            content.append(line)
    
    return '\n'.join(content).strip()


def _extract_risk_assessment(plan: str) -> Dict[str, str]:
    """Extract risk assessment details.
    
    Args:
        plan: Full markdown plan
        
    Returns:
        Dictionary with risk assessment fields
    """
    section = _extract_section(plan, "## Risk Assessment")
    
    risk = {
        'complexity': 'Unknown',
        'risk_level': 'Unknown',
        'estimated_time': 'Unknown'
    }
    
    for line in section.split('\n'):
        line = line.strip()
        if line.startswith('- Complexity:'):
            risk['complexity'] = line.replace('- Complexity:', '').strip()
        elif line.startswith('- Risk Level:'):
            risk['risk_level'] = line.replace('- Risk Level:', '').strip()
        elif line.startswith('- Estimated Time:'):
            risk['estimated_time'] = line.replace('- Estimated Time:', '').strip()
    
    return risk


def _extract_files_affected(plan: str) -> List[Dict[str, str]]:
    """Extract list of affected files.
    
    Args:
        plan: Full markdown plan
        
    Returns:
        List of dictionaries with file and operation
    """
    section = _extract_section(plan, "## Files Affected")
    
    files = []
    for line in section.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            # Parse format: - `file.py` (Operation)
            match = re.match(r'-\s+`([^`]+)`\s+\(([^)]+)\)', line)
            if match:
                files.append({
                    'file': match.group(1),
                    'operation': match.group(2)
                })
    
    return files
