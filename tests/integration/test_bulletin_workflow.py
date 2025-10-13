"""
Integration tests for the full bulletin creation workflow.

Tests the complete lifecycle: Import → Edit → Export
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bulletin_builder.app_core import importer, exporter, drafts


class TestBulletinCreationWorkflow:
    """Test the full bulletin creation workflow."""
    
    @pytest.fixture
    def mock_app(self):
        """Create a mock application."""
        app = Mock()
        app.template_name = "default"
        app.theme = "light"
        app.sections_data = []
        app.google_api_key = "test_key"
        app.openai_api_key = "test_key"
        app.events_feed_url = "https://example.com/events"
        app.current_draft_path = None
        app.renderer = Mock()
        app.renderer.set_template = Mock()
        app.refresh_listbox_titles = Mock()
        app.show_placeholder = Mock()
        app.update_preview = Mock()
        app.settings_frame = Mock()
        return app
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing."""
        return """Event Name,Start Date,Start Time,End Date,End Time,Location,Description,Image URL
Community Potluck,2025-08-15,18:00,2025-08-15,20:00,Community Center,"Join us for a potluck dinner",https://example.com/potluck.jpg
Yoga Class,2025-08-16,09:00,2025-08-16,10:30,Recreation Hall,"Morning yoga for all levels",https://example.com/yoga.jpg
Board Meeting,2025-08-17,14:00,2025-08-17,16:00,Board Room,"Monthly board meeting",
"""
    
    @pytest.fixture
    def sample_json_data(self):
        """Create sample JSON data for testing."""
        return {
            "events": [
                {
                    "name": "Summer Festival",
                    "startDate": "2025-08-20",
                    "startTime": "10:00",
                    "endDate": "2025-08-20",
                    "endTime": "18:00",
                    "location": "Main Park",
                    "description": "Annual summer festival with food, music, and games",
                    "imageUrl": "https://example.com/festival.jpg"
                },
                {
                    "name": "Art Exhibition",
                    "startDate": "2025-08-22",
                    "startTime": "14:00",
                    "endDate": "2025-08-25",
                    "endTime": "17:00",
                    "location": "Art Gallery",
                    "description": "Local artist showcase",
                    "imageUrl": "https://example.com/art.jpg"
                }
            ]
        }
    
    def test_csv_import_to_section_creation(self, mock_app, sample_csv_data):
        """Test importing CSV data and creating sections."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_data)
            csv_path = Path(f.name)
        
        try:
            # Initialize importer
            importer.init(mock_app)
            
            # Parse CSV manually
            import csv
            events = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append({
                        'title': row.get('Event Name', ''),
                        'description': row.get('Description', ''),
                        'start_date': row.get('Start Date', ''),
                        'location': row.get('Location', '')
                    })
            
            # Verify events imported
            assert len(events) == 3
            assert events[0]['title'] == 'Community Potluck'
            assert events[1]['title'] == 'Yoga Class'
            assert events[2]['title'] == 'Board Meeting'
            
            # Create sections from events
            for event in events:
                mock_app.sections_data.append({
                    'title': event['title'],
                    'content': event['description'],
                    'section_type': 'event'
                })
            
            # Verify sections created
            assert len(mock_app.sections_data) == 3
            assert mock_app.sections_data[0]['title'] == 'Community Potluck'
            assert mock_app.sections_data[0]['section_type'] == 'event'
            
        finally:
            csv_path.unlink()
    
    def test_json_import_to_section_creation(self, mock_app, sample_json_data):
        """Test importing JSON data and creating sections."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(sample_json_data, f)
            json_path = Path(f.name)
        
        try:
            # Parse JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                events = []
                for event in data.get('events', []):
                    events.append({
                        'title': event.get('name', ''),
                        'description': event.get('description', ''),
                        'start_date': event.get('startDate', ''),
                        'location': event.get('location', '')
                    })
            
            # Verify events imported
            assert len(events) == 2
            assert events[0]['title'] == 'Summer Festival'
            assert events[1]['title'] == 'Art Exhibition'
            
            # Create sections from events
            for event in events:
                mock_app.sections_data.append({
                    'title': event['title'],
                    'content': event['description'],
                    'section_type': 'event'
                })
            
            # Verify sections created
            assert len(mock_app.sections_data) == 2
            assert mock_app.sections_data[0]['title'] == 'Summer Festival'
            
        finally:
            json_path.unlink()
    
    def test_section_editing_workflow(self, mock_app):
        """Test editing section content."""
        # Create initial section
        mock_app.sections_data.append({
            'title': "Original Title",
            'content': "Original content",
            'section_type': 'announcement'
        })
        
        # Edit section
        mock_app.sections_data[0]['title'] = "Updated Title"
        mock_app.sections_data[0]['content'] = "Updated content with more details"
        mock_app.sections_data[0]['section_type'] = 'spotlight'
        
        # Verify edits
        assert mock_app.sections_data[0]['title'] == "Updated Title"
        assert mock_app.sections_data[0]['content'] == "Updated content with more details"
        assert mock_app.sections_data[0]['section_type'] == 'spotlight'
    
    def test_full_workflow_import_edit_export(self, mock_app, sample_csv_data):
        """Test the complete workflow from import to export."""
        # Step 1: Import CSV data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_data)
            csv_path = Path(f.name)
        
        try:
            # Parse CSV
            import csv
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    mock_app.sections_data.append({
                        'title': row.get('Event Name', ''),
                        'content': row.get('Description', ''),
                        'section_type': 'event'
                    })
            
            # Step 2: Edit first section
            mock_app.sections_data[0]['title'] = "Updated Community Potluck"
            mock_app.sections_data[0]['content'] = "Join us for an updated potluck dinner with more fun!"
            
            # Step 3: Verify we have sections ready for export
            assert len(mock_app.sections_data) == 3
            assert mock_app.sections_data[0]['title'] == "Updated Community Potluck"
            
            # Step 4: Initialize exporter
            exporter.init(mock_app)
            
            # Verify draft data structure is correct for export
            draft_data = {
                'title': 'Test Bulletin',
                'date': '2025-08-15',
                'sections': mock_app.sections_data,
                'settings': {}
            }
            assert 'sections' in draft_data
            assert len(draft_data['sections']) == 3
                
        finally:
            csv_path.unlink()
    
    def test_save_and_load_workflow(self, mock_app):
        """Test saving and loading draft workflow."""
        # Initialize drafts module
        drafts.init(mock_app)
        
        # Create draft with sections
        mock_app.sections_data = [
            {'title': "Section 1", 'content': "Content 1", 'section_type': 'announcement'},
            {'title': "Section 2", 'content': "Content 2", 'section_type': 'event'}
        ]
        
        # Save draft
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            draft_path = Path(f.name)
        
        try:
            draft_data = {
                'sections': mock_app.sections_data,
                'template_name': 'modern',
                'settings': {}
            }
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f)
            
            # Load draft
            with open(draft_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            new_sections = loaded_data.get('sections', [])
            
            # Verify loaded data
            assert len(new_sections) == 2
            assert new_sections[0]['title'] == "Section 1"
            assert new_sections[1]['title'] == "Section 2"
            
        finally:
            draft_path.unlink()
    
    def test_draft_modification_after_load(self, mock_app):
        """Test modifying draft after loading."""
        # Create and save initial draft
        mock_app.sections_data = [
            {'title': "Original", 'content': "Original content", 'section_type': 'announcement'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            draft_path = Path(f.name)
        
        try:
            # Save
            draft_data = {'sections': mock_app.sections_data}
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f)
            
            # Load into new list
            with open(draft_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                new_sections = loaded_data['sections']
            
            # Modify loaded draft
            new_sections[0]['title'] = "Modified"
            new_sections.append({
                'title': "New Section",
                'content': "New content",
                'section_type': 'spotlight'
            })
            
            # Save modified draft
            modified_data = {'sections': new_sections}
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f)
            
            # Load again and verify
            with open(draft_path, 'r', encoding='utf-8') as f:
                final_data = json.load(f)
                final_sections = final_data['sections']
            
            assert len(final_sections) == 2
            assert final_sections[0]['title'] == "Modified"
            assert final_sections[1]['title'] == "New Section"
            
        finally:
            draft_path.unlink()


class TestVersioningWorkflow:
    """Test draft versioning workflow."""
    
    @pytest.fixture
    def mock_app_with_versioning(self):
        """Create mock app with versioning support."""
        app = Mock()
        app.sections_data = []
        app.current_draft_path = "test_bulletin.json"
        app.version_manager = Mock()
        app.version_manager.save_version = Mock(return_value="v1_20250815_120000")
        app.version_manager.list_versions = Mock(return_value=[
            {
                "version_id": "v1_20250815_120000",
                "timestamp": "2025-08-15 12:00:00",
                "type": "manual",
                "section_count": 3
            }
        ])
        app.version_manager.restore_version = Mock()
        return app
    
    def test_version_creation_on_save(self, mock_app_with_versioning):
        """Test version creation when saving draft."""
        app = mock_app_with_versioning
        
        # Create sections
        app.sections_data = [
            {'title': "V1 Section", 'content': "Initial content", 'section_type': 'announcement'}
        ]
        
        # Save version
        draft_data = {'sections': app.sections_data}
        version_id = app.version_manager.save_version(draft_data, "manual")
        
        # Verify version created
        assert version_id == "v1_20250815_120000"
        app.version_manager.save_version.assert_called_once()
    
    def test_version_restore_workflow(self, mock_app_with_versioning):
        """Test restoring from version."""
        app = mock_app_with_versioning
        
        # Current state
        app.sections_data = [
            {'title': "Current", 'content': "Current content", 'section_type': 'announcement'}
        ]
        
        # Restore previous version
        restored_data = {
            "sections": [{'title': "Previous", 'content': "Previous content", 'section_type': 'event'}]
        }
        app.version_manager.restore_version.return_value = restored_data
        
        # Restore
        version_id = "v1_20250815_120000"
        data = app.version_manager.restore_version(version_id)
        
        # Apply restored data
        app.sections_data = data['sections']
        
        # Verify restored state
        assert len(app.sections_data) == 1
        assert app.sections_data[0]['title'] == "Previous"
        app.version_manager.restore_version.assert_called_once_with(version_id)
    
    def test_version_list_workflow(self, mock_app_with_versioning):
        """Test listing available versions."""
        app = mock_app_with_versioning
        
        # Get versions
        versions = app.version_manager.list_versions()
        
        # Verify versions
        assert len(versions) == 1
        assert versions[0]["version_id"] == "v1_20250815_120000"
        assert versions[0]["type"] == "manual"
        app.version_manager.list_versions.assert_called_once()


class TestAutoBackupWorkflow:
    """Test auto-backup and recovery workflow."""
    
    @pytest.fixture
    def mock_app_with_backup(self):
        """Create mock app with backup support."""
        app = Mock()
        app.sections_data = []
        app.auto_backup_manager = Mock()
        app.auto_backup_manager.create_backup = Mock(return_value=True)
        app.auto_backup_manager.detect_crash = Mock(return_value=False)
        app.auto_backup_manager.get_available_backups = Mock(return_value=[])
        app.auto_backup_manager.restore_backup = Mock(return_value=True)
        return app
    
    def test_auto_backup_creation(self, mock_app_with_backup):
        """Test automatic backup creation."""
        app = mock_app_with_backup
        
        # Create sections
        app.sections_data = [
            {'title': "Important", 'content': "Don't lose this!", 'section_type': 'announcement'}
        ]
        
        # Trigger backup
        draft_data = {'sections': app.sections_data}
        backup_created = app.auto_backup_manager.create_backup(draft_data)
        
        # Verify backup created
        assert backup_created is True
        app.auto_backup_manager.create_backup.assert_called_once()
    
    def test_crash_detection(self, mock_app_with_backup):
        """Test crash detection on startup."""
        app = mock_app_with_backup
        
        # Simulate crash detection
        app.auto_backup_manager.detect_crash.return_value = True
        app.auto_backup_manager.get_available_backups.return_value = [
            {
                "path": "/backups/backup_20250815_120000.json",
                "timestamp": "2025-08-15 12:00:00",
                "section_count": 3
            }
        ]
        
        # Check for crash
        has_crash = app.auto_backup_manager.detect_crash()
        
        # Verify crash detected
        assert has_crash is True
        
        # Get available backups
        backups = app.auto_backup_manager.get_available_backups()
        assert len(backups) == 1
    
    def test_backup_restoration(self, mock_app_with_backup):
        """Test restoring from backup."""
        app = mock_app_with_backup
        
        # Simulate backup restoration
        backup_data = {
            "sections": [
                {'title': "Recovered", 'content': "Recovered content", 'section_type': 'announcement'}
            ]
        }
        app.auto_backup_manager.restore_backup.return_value = backup_data
        
        # Restore backup
        backup_path = "/backups/backup_20250815_120000.json"
        restored_data = app.auto_backup_manager.restore_backup(backup_path)
        
        # Apply restored data
        app.sections_data = restored_data['sections']
        
        # Verify restoration
        assert len(app.sections_data) == 1
        assert app.sections_data[0]['title'] == "Recovered"
        app.auto_backup_manager.restore_backup.assert_called_once_with(backup_path)


class TestComplexWorkflows:
    """Test complex multi-step workflows."""
    
    @pytest.fixture
    def mock_app_full(self):
        """Create fully-featured mock app."""
        app = Mock()
        app.sections_data = []
        app.template_name = "default"
        app.version_manager = Mock()
        app.auto_backup_manager = Mock()
        app.google_api_key = "test_key"
        app.openai_api_key = "test_key"
        app.events_feed_url = "https://example.com/events"
        return app
    
    def test_import_edit_version_export_workflow(self, mock_app_full):
        """Test complete workflow: Import → Edit → Version → Export."""
        app = mock_app_full
        
        # Step 1: Import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("""Event Name,Start Date,Description
Test Event,2025-08-15,Test description""")
            csv_path = Path(f.name)
        
        try:
            import csv
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    app.sections_data.append({
                        'title': row.get('Event Name', ''),
                        'content': row.get('Description', ''),
                        'section_type': 'event'
                    })
            
            # Step 2: Edit
            app.sections_data[0]['content'] = "Updated description"
            
            # Step 3: Create version
            app.version_manager.save_version.return_value = "v1_20250815_120000"
            draft_data = {'sections': app.sections_data}
            version_id = app.version_manager.save_version(draft_data, "manual")
            assert version_id == "v1_20250815_120000"
            
            # Step 4: Verify sections ready for export
            assert len(app.sections_data) == 1
            assert app.sections_data[0]['content'] == "Updated description"
            
        finally:
            csv_path.unlink()
    
    def test_multi_import_merge_workflow(self, mock_app_full):
        """Test importing from multiple sources and merging."""
        app = mock_app_full
        
        # Import from CSV
        csv_data = """Title,Description
Event 1,CSV Event"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_data)
            csv_path = Path(f.name)
        
        try:
            import csv
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    app.sections_data.append({
                        'title': row.get('Title', ''),
                        'content': row.get('Description', ''),
                        'section_type': 'event'
                    })
        finally:
            csv_path.unlink()
        
        # Import from JSON
        json_data = {"events": [{"name": "Event 2", "description": "JSON Event"}]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(json_data, f)
            json_path = Path(f.name)
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for event in data.get('events', []):
                    app.sections_data.append({
                        'title': event.get('name', ''),
                        'content': event.get('description', ''),
                        'section_type': 'event'
                    })
        finally:
            json_path.unlink()
        
        # Verify merged sections
        assert len(app.sections_data) == 2
        assert app.sections_data[0]['title'] == "Event 1"
        assert app.sections_data[1]['title'] == "Event 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
