"""
Tests for draft versioning system.
"""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from bulletin_builder.app_core.draft_versioning import DraftVersionManager, VersionInfo


@pytest.fixture
def temp_draft_dir():
    """Create a temporary directory for draft testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_draft_data():
    """Sample draft data for testing."""
    return {
        "title": "Test Bulletin",
        "date": "2025-10-10",
        "sections": [
            {"type": "announcements", "title": "Announcements", "content": []},
            {"type": "events", "title": "Events", "content": []},
            {"type": "text", "title": "Notes", "content": "Some text"}
        ],
        "settings": {
            "colors": {"primary": "#103040"}
        }
    }


@pytest.fixture
def draft_path(temp_draft_dir, sample_draft_data):
    """Create a test draft file."""
    draft_file = temp_draft_dir / "test_bulletin.json"
    with open(draft_file, 'w') as f:
        json.dump(sample_draft_data, f)
    return draft_file


@pytest.fixture
def version_manager(draft_path):
    """Create a version manager instance."""
    return DraftVersionManager(str(draft_path))


class TestDraftVersionManager:
    """Test DraftVersionManager initialization and basic operations."""
    
    def test_initialization(self, version_manager, draft_path):
        """Test version manager initialization."""
        assert version_manager.draft_path == Path(draft_path)
        assert version_manager.draft_name == "test_bulletin"
        assert version_manager.versions_dir.exists()
        assert version_manager.versions_dir.name == version_manager.draft_name
    
    def test_versions_directory_created(self, version_manager):
        """Test that versions directory is created."""
        assert version_manager.versions_dir.exists()
        assert version_manager.versions_dir.is_dir()
    
    def test_save_version(self, version_manager, sample_draft_data):
        """Test saving a version."""
        version_id = version_manager.save_version(
            sample_draft_data,
            description="Test version",
            auto=False
        )
        
        assert version_id is not None
        assert version_manager.version_exists(version_id)
    
    def test_version_metadata_saved(self, version_manager, sample_draft_data):
        """Test that version metadata is saved correctly."""
        description = "Test version with metadata"
        version_id = version_manager.save_version(
            sample_draft_data,
            description=description,
            auto=False
        )
        
        # Check metadata file exists
        version_file = version_manager.versions_dir / f"test_bulletin_v{version_id}.json"
        meta_file = Path(str(version_file) + version_manager.METADATA_SUFFIX)
        
        assert meta_file.exists()
        
        # Check metadata content
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        assert metadata['version_id'] == version_id
        assert metadata['description'] == description
        assert metadata['auto_created'] is False
        assert metadata['sections_count'] == 3
    
    def test_list_versions_empty(self, version_manager):
        """Test listing versions when none exist."""
        versions = version_manager.list_versions()
        assert versions == []
    
    def test_list_versions_multiple(self, version_manager, sample_draft_data):
        """Test listing multiple versions."""
        # Create 3 versions
        v1 = version_manager.save_version(sample_draft_data, "Version 1", auto=False)
        v2 = version_manager.save_version(sample_draft_data, "Version 2", auto=True)
        v3 = version_manager.save_version(sample_draft_data, "Version 3", auto=False)
        
        versions = version_manager.list_versions()
        
        assert len(versions) == 3
        # Should be sorted newest first
        assert versions[0].version_id == v3
        assert versions[1].version_id == v2
        assert versions[2].version_id == v1
    
    def test_restore_version(self, version_manager, sample_draft_data):
        """Test restoring a version."""
        # Modify draft data for version
        modified_data = sample_draft_data.copy()
        modified_data['title'] = "Modified Title"
        
        version_id = version_manager.save_version(
            modified_data,
            description="Modified version"
        )
        
        # Restore the version
        restored_data = version_manager.restore_version(version_id)
        
        assert restored_data['title'] == "Modified Title"
        assert len(restored_data['sections']) == 3
    
    def test_restore_nonexistent_version(self, version_manager):
        """Test restoring a version that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            version_manager.restore_version("99999999_999999")
    
    def test_delete_version(self, version_manager, sample_draft_data):
        """Test deleting a version."""
        version_id = version_manager.save_version(
            sample_draft_data,
            description="To be deleted"
        )
        
        assert version_manager.version_exists(version_id)
        
        version_manager.delete_version(version_id)
        
        assert not version_manager.version_exists(version_id)
    
    def test_cleanup_old_versions(self, version_manager, sample_draft_data):
        """Test cleanup of old versions."""
        # Create 25 versions
        version_ids = []
        for i in range(25):
            vid = version_manager.save_version(
                sample_draft_data,
                description=f"Version {i}",
                auto=True
            )
            version_ids.append(vid)
        
        # Cleanup should keep only 20 newest
        version_manager.cleanup_old_versions(keep_count=20)
        
        versions = version_manager.list_versions()
        assert len(versions) == 20
        
        # Oldest 5 should be deleted
        for vid in version_ids[:5]:
            assert not version_manager.version_exists(vid)
        
        # Newest 20 should exist
        for vid in version_ids[5:]:
            assert version_manager.version_exists(vid)
    
    def test_get_version_info(self, version_manager, sample_draft_data):
        """Test getting version metadata."""
        description = "Test version info"
        version_id = version_manager.save_version(
            sample_draft_data,
            description=description,
            auto=False
        )
        
        info = version_manager.get_version_info(version_id)
        
        assert info is not None
        assert info.version_id == version_id
        assert info.description == description
        assert info.auto_created is False
        assert info.sections_count == 3
    
    def test_get_version_info_nonexistent(self, version_manager):
        """Test getting info for nonexistent version."""
        info = version_manager.get_version_info("99999999_999999")
        assert info is None
    
    def test_create_auto_version(self, version_manager, sample_draft_data):
        """Test creating an automatic version."""
        version_id = version_manager.create_auto_version(
            sample_draft_data,
            trigger="section-change"
        )
        
        assert version_id is not None
        
        info = version_manager.get_version_info(version_id)
        assert info.auto_created is True
        assert "Auto-save (section-change)" in info.description
    
    def test_version_file_structure(self, version_manager, sample_draft_data):
        """Test the structure of created version files."""
        version_id = version_manager.save_version(
            sample_draft_data,
            description="Structure test"
        )
        
        version_file = version_manager.versions_dir / f"test_bulletin_v{version_id}.json"
        
        assert version_file.exists()
        
        with open(version_file, 'r') as f:
            data = json.load(f)
        
        assert data['title'] == sample_draft_data['title']
        assert len(data['sections']) == len(sample_draft_data['sections'])


class TestVersionInfo:
    """Test VersionInfo dataclass."""
    
    def test_version_info_creation(self):
        """Test creating a VersionInfo object."""
        info = VersionInfo(
            version_id="20251010_163045",
            parent_draft="test.json",
            timestamp="2025-10-10T16:30:45",
            description="Test version",
            auto_created=False,
            sections_count=3,
            file_size=1024,
            version_path="/path/to/version.json"
        )
        
        assert info.version_id == "20251010_163045"
        assert info.description == "Test version"
        assert info.auto_created is False
    
    def test_version_info_to_dict(self):
        """Test converting VersionInfo to dictionary."""
        info = VersionInfo(
            version_id="20251010_163045",
            parent_draft="test.json",
            timestamp="2025-10-10T16:30:45",
            description="Test",
            auto_created=True,
            sections_count=5,
            file_size=2048,
            version_path="/path/to/version.json"
        )
        
        data = info.to_dict()
        
        assert data['version_id'] == "20251010_163045"
        assert data['auto_created'] is True
        assert data['sections_count'] == 5
    
    def test_version_info_from_dict(self):
        """Test creating VersionInfo from dictionary."""
        data = {
            'version_id': "20251010_163045",
            'parent_draft': "test.json",
            'timestamp': "2025-10-10T16:30:45",
            'description': "Test",
            'auto_created': False,
            'sections_count': 3,
            'file_size': 1024,
            'version_path': "/path/to/version.json"
        }
        
        info = VersionInfo.from_dict(data)
        
        assert info.version_id == "20251010_163045"
        assert info.auto_created is False
    
    def test_get_display_name(self):
        """Test getting display name."""
        info = VersionInfo(
            version_id="20251010_163045",
            parent_draft="test.json",
            timestamp="2025-10-10T16:30:45",
            description="Important save",
            auto_created=False,
            sections_count=3,
            file_size=1024,
            version_path="/path/to/version.json"
        )
        
        display_name = info.get_display_name()
        
        assert "2025-10-10" in display_name
        assert "Important save" in display_name
        assert "[auto]" not in display_name
    
    def test_get_display_name_auto(self):
        """Test display name for auto-created version."""
        info = VersionInfo(
            version_id="20251010_163045",
            parent_draft="test.json",
            timestamp="2025-10-10T16:30:45",
            description="Auto-save",
            auto_created=True,
            sections_count=3,
            file_size=1024,
            version_path="/path/to/version.json"
        )
        
        display_name = info.get_display_name()
        
        assert "[auto]" in display_name


class TestVersionManagerIntegration:
    """Integration tests for version manager."""
    
    def test_full_workflow(self, version_manager, sample_draft_data):
        """Test complete workflow: save, list, restore."""
        # Save initial version
        v1_id = version_manager.save_version(
            sample_draft_data,
            description="Initial version"
        )
        
        # Modify and save another version
        modified_data = sample_draft_data.copy()
        modified_data['title'] = "Updated Title"
        modified_data['sections'].append({
            'type': 'text',
            'title': 'New Section',
            'content': 'New content'
        })
        
        v2_id = version_manager.save_version(
            modified_data,
            description="Added section"
        )
        
        # List versions
        versions = version_manager.list_versions()
        assert len(versions) == 2
        assert versions[0].version_id == v2_id
        assert versions[0].sections_count == 4
        assert versions[1].version_id == v1_id
        assert versions[1].sections_count == 3
        
        # Restore first version
        restored = version_manager.restore_version(v1_id)
        assert restored['title'] == "Test Bulletin"
        assert len(restored['sections']) == 3
    
    def test_missing_metadata_recovery(self, version_manager, sample_draft_data):
        """Test recovery when metadata file is missing."""
        # Save a version
        version_id = version_manager.save_version(sample_draft_data, "Test")
        
        # Delete metadata file
        version_file = version_manager.versions_dir / f"test_bulletin_v{version_id}.json"
        meta_file = Path(str(version_file) + version_manager.METADATA_SUFFIX)
        meta_file.unlink()
        
        # List versions should recreate metadata
        versions = version_manager.list_versions()
        
        assert len(versions) == 1
        assert versions[0].version_id == version_id
        
        # Metadata file should be recreated
        assert meta_file.exists()
    
    def test_concurrent_version_creation(self, version_manager, sample_draft_data):
        """Test creating multiple versions rapidly."""
        version_ids = []
        
        # Create 10 versions rapidly
        for i in range(10):
            vid = version_manager.save_version(
                sample_draft_data,
                description=f"Rapid version {i}"
            )
            version_ids.append(vid)
        
        # All should be unique
        assert len(set(version_ids)) == 10
        
        # All should be listable
        versions = version_manager.list_versions()
        assert len(versions) == 10
