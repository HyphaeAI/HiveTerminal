"""HiveTerminal textual UI wrapper.

This module provides a wrapper around Vibe's textual UI that replaces
the banner with HiveTerminal branding.
"""

from __future__ import annotations

from vibe.cli.textual_ui.app import VibeApp, _print_session_resume_message
from vibe.cli.plan_offer.adapters.http_whoami_gateway import HttpWhoAmIGateway
from vibe.cli.update_notifier import (
    FileSystemUpdateCacheRepository,
    PyPIUpdateGateway,
)
from vibe.core.agent_loop import AgentLoop


def run_hive_textual_ui(
    agent_loop: AgentLoop,
    initial_prompt: str | None = None,
    teleport_on_start: bool = False,
    mode: str = "conversational",
) -> None:
    """Run HiveTerminal textual UI with custom branding.
    
    This function wraps Vibe's run_textual_ui and replaces the banner
    with HiveTerminal branding by updating the banner text after mount.
    
    Args:
        agent_loop: The agent loop to use
        initial_prompt: Optional initial prompt to send
        teleport_on_start: Whether to start teleport on startup
        mode: The current mode (conversational or spec)
    """
    update_notifier = PyPIUpdateGateway(project_name="mistral-vibe")
    update_cache_repository = FileSystemUpdateCacheRepository()
    plan_offer_gateway = HttpWhoAmIGateway()
    
    app = VibeApp(
        agent_loop=agent_loop,
        initial_prompt=initial_prompt,
        teleport_on_start=teleport_on_start,
        update_notifier=update_notifier,
        update_cache_repository=update_cache_repository,
        plan_offer_gateway=plan_offer_gateway,
    )
    
    # Store mode for banner update
    app._hive_mode = mode
    
    # Monkey-patch the on_mount to update banner text after it's created
    original_on_mount = app.on_mount
    
    async def hive_on_mount():
        """Custom on_mount that updates the banner text to HiveTerminal."""
        # Call original on_mount first
        await original_on_mount()
        
        # Now update the banner text
        try:
            from vibe.cli.textual_ui.widgets.no_markup_static import NoMarkupStatic
            
            # Update the banner brand text
            banner_brand = app.query_one("#banner-brand", NoMarkupStatic)
            banner_brand.update("HiveTerminal")
            
            # Update the meta counts to include mode
            if app._banner:
                original_format = app._banner._format_meta_counts
                
                def hive_format_meta_counts():
                    mode_display = f"[{mode.title()}]"
                    original_text = original_format()
                    return f"{mode_display} · {original_text}"
                
                app._banner._format_meta_counts = hive_format_meta_counts
                # Trigger a state update to refresh the display
                app._banner.watch_state()
                
        except Exception as e:
            # If banner update fails, just continue with Vibe banner
            pass
    
    # Replace on_mount
    app.on_mount = hive_on_mount
    
    session_id = app.run()
    _print_session_resume_message(session_id)
