import json
from pathlib import Path
from tkinter import filedialog, messagebox
from datetime import date
from typing import Dict, Any, Optional
from bulletin_builder.exceptions import DraftLoadError, DraftSaveError, JSONImportError
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)

def init(app: Any) -> None:
    """
    Initialize draft management functions.
    
    Attaches new_draft, open_draft, and save_draft functions to the app.
    
    Args:
        app: The main application instance
    """
    def _default_settings() -> Dict[str, Any]:
        """Get default bulletin settings."""
        return {
            'bulletin_title': 'LACC Bulletin',
            'bulletin_date': date.today().strftime('%A, %B %d, %Y'),
            'theme_css': 'default.css',
            'appearance_mode': 'Dark',
            'colors': {'primary':'#103040','secondary':'#506070'},
            'google_api_key': app.google_api_key,
            'events_feed_url': app.events_feed_url
        }

    def new_draft() -> None:
        """Create a new draft, discarding current content."""
        if messagebox.askyesno('New Draft','Discard current draft and start new?', parent=app):
            app.sections_data.clear()
            app.current_draft_path = None
            if hasattr(app.settings_frame,'load_data'):
                app.settings_frame.load_data(
                    _default_settings(),
                    app.google_api_key,
                    app.openai_api_key,
                    app.events_feed_url,
                )
            app.renderer.set_template('main_layout.html')
            app.refresh_listbox_titles()
            app.show_placeholder()
            app.update_preview()
            
    def open_draft() -> None:
        """Open an existing draft from a JSON file."""
        path = filedialog.askopenfilename(
            defaultextension='.json', filetypes=[('Drafts','*.json')],
            initialdir='./user_drafts', title='Open Draft', parent=app
        )
        if not path:
            return
        try:
            logger.info(f"Opening draft from {path}")
            text = Path(path).read_text(encoding='utf-8')
            data = json.loads(text)
        except FileNotFoundError as e:
            logger.error(f"Draft file not found: {path}")
            error = DraftLoadError(f"Draft file not found: {Path(path).name}", file_path=path)
            messagebox.showerror('Open Error', str(error), parent=app)
            return
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in draft file: {e}")
            error = JSONImportError(f"Invalid JSON format in draft file: {e.msg}", file_path=path)
            messagebox.showerror('Open Error', str(error), parent=app)
            return
        except Exception as e:
            logger.exception(f"Unexpected error opening draft: {e}")
            error = DraftLoadError(f"Failed to open draft: {str(e)}", file_path=path)
            messagebox.showerror('Open Error', str(error), parent=app)
            return
        
        logger.debug(f"Draft loaded with {len(data.get('sections', []))} sections")
        app.sections_data[:] = data.get('sections',[])
        app.current_draft_path = path
        app.renderer.set_template(data.get('template_name', 'main_layout.html'))
        settings = data.get('settings', _default_settings())
        if hasattr(app.settings_frame,'load_data'):
            app.settings_frame.load_data(
                settings,
                settings.get('google_api_key', app.google_api_key),
                settings.get('openai_api_key', app.openai_api_key),
                settings.get('events_feed_url', app.events_feed_url),
            )
        app.refresh_listbox_titles()
        app.show_placeholder()
        app.update_preview()
        
    def save_draft(save_as: bool = False) -> None:
        """
        Save the current draft to a JSON file.
        
        Args:
            save_as: If True, always prompt for a new file location
        """
        if not app.current_draft_path or save_as:
            path = filedialog.asksaveasfilename(
                defaultextension='.json', filetypes=[('Drafts','*.json')],
                initialdir='./user_drafts', title='Save Draft As', parent=app
            )
            if not path:
                return
            app.current_draft_path = path
        
        payload: Dict[str, Any] = {
            'sections': app.sections_data,
            'settings': app.settings_frame.dump(),
            'template_name': app.renderer.template_name
        }
        
        try:
            logger.info(f"Saving draft to {app.current_draft_path}")
            draft_path = Path(app.current_draft_path)
            
            # Ensure parent directory exists
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a version before saving (if draft already exists)
            if draft_path.exists():
                try:
                    from bulletin_builder.app_core.draft_versioning import DraftVersionManager
                    manager = DraftVersionManager(draft_path)
                    
                    # Read current draft data
                    current_data = json.loads(draft_path.read_text(encoding='utf-8'))
                    
                    # Create auto-version
                    manager.create_auto_version(current_data, trigger="manual-save")
                    logger.debug(f"Created auto-version before save")
                except Exception as e:
                    # Don't fail the save if versioning fails
                    logger.warning(f"Failed to create version before save: {e}")
            
            # Write the file
            draft_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            
            logger.debug(f"Draft saved with {len(app.sections_data)} sections")
            app.show_status_message(f"Draft saved: {draft_path.name}")
            
        except PermissionError as e:
            logger.error(f"Permission denied saving draft: {e}")
            error = DraftSaveError(
                f"Permission denied: Cannot write to {draft_path.name}",
                file_path=str(draft_path)
            )
            messagebox.showerror('Save Error', str(error), parent=app)
            
        except OSError as e:
            logger.error(f"OS error saving draft: {e}")
            error = DraftSaveError(
                f"Failed to save draft: {str(e)}",
                file_path=str(draft_path)
            )
            messagebox.showerror('Save Error', str(error), parent=app)
            
        except Exception as e:
            logger.exception(f"Unexpected error saving draft: {e}")
            error = DraftSaveError(
                f"Unexpected error saving draft: {str(e)}",
                file_path=str(draft_path)
            )
            messagebox.showerror('Save Error', str(error), parent=app)
    
    def show_version_history() -> None:
        """Show version history dialog for current draft."""
        if not app.current_draft_path:
            messagebox.showinfo(
                'No Draft Loaded',
                'Please open or save a draft before viewing version history.',
                parent=app
            )
            return
        
        try:
            from bulletin_builder.ui.version_history_dialog import VersionHistoryDialog
            
            def on_restore(draft_data: dict):
                """Handle version restoration."""
                # Load the restored data into the app
                app.sections_data[:] = draft_data.get('sections', [])
                
                # Load settings
                settings = draft_data.get('settings', _default_settings())
                if hasattr(app.settings_frame, 'load_data'):
                    app.settings_frame.load_data(
                        settings,
                        settings.get('google_api_key', app.google_api_key),
                        settings.get('openai_api_key', app.openai_api_key),
                        settings.get('events_feed_url', app.events_feed_url),
                    )
                
                # Update template
                app.renderer.set_template(draft_data.get('template_name', 'main_layout.html'))
                
                # Refresh UI
                app.refresh_listbox_titles()
                app.show_placeholder()
                app.update_preview()
                
                logger.info("Version restored and loaded into application")
            
            # Show dialog
            dialog = VersionHistoryDialog(
                parent=app,
                draft_path=Path(app.current_draft_path),
                on_restore=on_restore
            )
            
        except Exception as e:
            logger.exception(f"Failed to show version history: {e}")
            messagebox.showerror(
                'Version History Error',
                f"Failed to open version history:\n{str(e)}",
                parent=app
            )

    app.new_draft  = new_draft
    app.open_draft = open_draft
    app.save_draft = save_draft
    app.show_version_history = show_version_history
