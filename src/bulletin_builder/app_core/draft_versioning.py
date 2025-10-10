"""
Draft versioning system for bulletin builder.

Provides version control for bulletin drafts, allowing users to:
- Save versions manually or automatically
- View version history
- Restore previous versions
- Compare versions (future enhancement)
"""

import json
import os
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from bulletin_builder.app_core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class VersionInfo:
    """Metadata about a draft version."""
    version_id: str
    parent_draft: str
    timestamp: str
    description: str
    auto_created: bool
    sections_count: int
    file_size: int
    version_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionInfo':
        """Create from dictionary."""
        return cls(**data)
    
    def get_display_name(self) -> str:
        """Get user-friendly display name."""
        dt = datetime.fromisoformat(self.timestamp)
        time_str = dt.strftime("%Y-%m-%d %I:%M:%S %p")
        auto_tag = " [auto]" if self.auto_created else ""
        desc = f" - {self.description}" if self.description else ""
        return f"{time_str}{auto_tag}{desc}"


class DraftVersionManager:
    """Manages version history for bulletin drafts."""
    
    VERSION_DIR_NAME = "versions"
    MAX_VERSIONS_DEFAULT = 20
    METADATA_SUFFIX = ".meta.json"
    
    def __init__(self, draft_path: str):
        """
        Initialize version manager for a draft.
        
        Args:
            draft_path: Path to the main draft file
        """
        self.draft_path = Path(draft_path)
        self.draft_dir = self.draft_path.parent
        self.draft_name = self.draft_path.stem
        self.versions_dir = self.draft_dir / self.VERSION_DIR_NAME / self.draft_name
        
        # Create versions directory if it doesn't exist
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DraftVersionManager initialized for: {self.draft_path}")
        logger.debug(f"Versions directory: {self.versions_dir}")
    
    def save_version(
        self,
        draft_data: Dict[str, Any],
        description: str = "",
        auto: bool = False
    ) -> str:
        """
        Save a new version of the draft.
        
        Args:
            draft_data: The draft content to version
            description: User-provided description (optional)
            auto: Whether this is an automatic version
            
        Returns:
            The version ID (timestamp-based)
        """
        # Generate version ID (timestamp with microseconds for uniqueness)
        timestamp = datetime.now()
        version_id = timestamp.strftime("%Y%m%d_%H%M%S_") + f"{timestamp.microsecond:06d}"
        
        # Create version filename
        version_filename = f"{self.draft_name}_v{version_id}.json"
        version_path = self.versions_dir / version_filename
        
        # Count sections
        sections_count = len(draft_data.get('sections', []))
        
        # Save the draft content
        try:
            with open(version_path, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, indent=2, ensure_ascii=False)
            
            file_size = version_path.stat().st_size
            
            # Create metadata
            metadata = VersionInfo(
                version_id=version_id,
                parent_draft=self.draft_path.name,
                timestamp=timestamp.isoformat(),
                description=description,
                auto_created=auto,
                sections_count=sections_count,
                file_size=file_size,
                version_path=str(version_path)
            )
            
            # Save metadata
            meta_path = version_path.with_suffix(version_path.suffix + self.METADATA_SUFFIX)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2)
            
            logger.info(f"Created version {version_id} ({'auto' if auto else 'manual'}): {description}")
            
            # Cleanup old versions
            self.cleanup_old_versions()
            
            return version_id
            
        except Exception as e:
            logger.error(f"Failed to save version: {e}", exc_info=True)
            raise
    
    def list_versions(self) -> List[VersionInfo]:
        """
        Get all versions sorted by timestamp (newest first).
        
        Returns:
            List of VersionInfo objects
        """
        versions = []
        
        try:
            # Find all version files
            version_files = list(self.versions_dir.glob(f"{self.draft_name}_v*.json"))
            
            for version_file in version_files:
                # Skip metadata files
                if version_file.suffix == self.METADATA_SUFFIX or \
                   str(version_file).endswith(f".json{self.METADATA_SUFFIX}"):
                    continue
                
                # Try to load metadata
                meta_path = Path(str(version_file) + self.METADATA_SUFFIX)
                
                if meta_path.exists():
                    try:
                        with open(meta_path, 'r', encoding='utf-8') as f:
                            meta_data = json.load(f)
                        versions.append(VersionInfo.from_dict(meta_data))
                    except Exception as e:
                        logger.warning(f"Failed to load metadata for {version_file}: {e}")
                else:
                    # Create metadata from file if missing
                    logger.warning(f"Metadata missing for {version_file}, creating from file")
                    try:
                        with open(version_file, 'r', encoding='utf-8') as f:
                            draft_data = json.load(f)
                        
                        # Extract version ID from filename
                        version_id = version_file.stem.split('_v')[-1]
                        
                        # Create minimal metadata
                        metadata = VersionInfo(
                            version_id=version_id,
                            parent_draft=self.draft_path.name,
                            timestamp=datetime.fromtimestamp(version_file.stat().st_mtime).isoformat(),
                            description="",
                            auto_created=True,
                            sections_count=len(draft_data.get('sections', [])),
                            file_size=version_file.stat().st_size,
                            version_path=str(version_file)
                        )
                        
                        # Save metadata for future use
                        with open(meta_path, 'w', encoding='utf-8') as f:
                            json.dump(metadata.to_dict(), f, indent=2)
                        
                        versions.append(metadata)
                    except Exception as e:
                        logger.error(f"Failed to recover metadata for {version_file}: {e}")
            
            # Sort by timestamp (newest first)
            versions.sort(key=lambda v: v.timestamp, reverse=True)
            
            logger.debug(f"Found {len(versions)} versions for {self.draft_name}")
            return versions
            
        except Exception as e:
            logger.error(f"Failed to list versions: {e}", exc_info=True)
            return []
    
    def restore_version(self, version_id: str) -> Dict[str, Any]:
        """
        Restore draft data from a specific version.
        
        Args:
            version_id: The version ID to restore
            
        Returns:
            The draft data from that version
            
        Raises:
            FileNotFoundError: If version doesn't exist
            ValueError: If version data is invalid
        """
        # Find the version file
        version_filename = f"{self.draft_name}_v{version_id}.json"
        version_path = self.versions_dir / version_filename
        
        if not version_path.exists():
            raise FileNotFoundError(f"Version {version_id} not found")
        
        try:
            with open(version_path, 'r', encoding='utf-8') as f:
                draft_data = json.load(f)
            
            logger.info(f"Restored version {version_id}")
            return draft_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in version {version_id}: {e}")
            raise ValueError(f"Version {version_id} contains invalid data")
        except Exception as e:
            logger.error(f"Failed to restore version {version_id}: {e}", exc_info=True)
            raise
    
    def delete_version(self, version_id: str) -> None:
        """
        Delete a specific version.
        
        Args:
            version_id: The version ID to delete
        """
        version_filename = f"{self.draft_name}_v{version_id}.json"
        version_path = self.versions_dir / version_filename
        meta_path = Path(str(version_path) + self.METADATA_SUFFIX)
        
        try:
            if version_path.exists():
                version_path.unlink()
                logger.info(f"Deleted version file: {version_path}")
            
            if meta_path.exists():
                meta_path.unlink()
                logger.debug(f"Deleted metadata file: {meta_path}")
            
        except Exception as e:
            logger.error(f"Failed to delete version {version_id}: {e}", exc_info=True)
            raise
    
    def cleanup_old_versions(self, keep_count: int = MAX_VERSIONS_DEFAULT) -> None:
        """
        Remove old versions, keeping only the most recent ones.
        
        Args:
            keep_count: Number of versions to keep (default: 20)
        """
        versions = self.list_versions()
        
        if len(versions) <= keep_count:
            return
        
        # Delete oldest versions
        versions_to_delete = versions[keep_count:]
        
        for version in versions_to_delete:
            try:
                self.delete_version(version.version_id)
                logger.info(f"Cleaned up old version: {version.version_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup version {version.version_id}: {e}")
    
    def get_version_info(self, version_id: str) -> Optional[VersionInfo]:
        """
        Get metadata for a specific version.
        
        Args:
            version_id: The version ID
            
        Returns:
            VersionInfo object or None if not found
        """
        versions = self.list_versions()
        for version in versions:
            if version.version_id == version_id:
                return version
        return None
    
    def create_auto_version(
        self,
        draft_data: Dict[str, Any],
        trigger: str = "auto-save"
    ) -> Optional[str]:
        """
        Create an automatic version with a standard description.
        
        Args:
            draft_data: The draft content
            trigger: What triggered the auto-save
            
        Returns:
            Version ID or None if failed
        """
        try:
            description = f"Auto-save ({trigger})"
            return self.save_version(draft_data, description=description, auto=True)
        except Exception as e:
            logger.error(f"Auto-version creation failed: {e}")
            return None
    
    def get_versions_directory(self) -> Path:
        """Get the path to the versions directory."""
        return self.versions_dir
    
    def version_exists(self, version_id: str) -> bool:
        """Check if a version exists."""
        version_filename = f"{self.draft_name}_v{version_id}.json"
        version_path = self.versions_dir / version_filename
        return version_path.exists()
