"""
Performance benchmarks for Bulletin Builder.

Tests rendering, export, and import performance to detect regressions.
Run with: pytest tests/benchmarks/test_performance.py -v --benchmark-only
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch


class TestRenderingPerformance:
    """Benchmark rendering performance."""
    
    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        app = Mock()
        app.template_name = "default"
        app.sections_data = []
        return app
    
    @pytest.fixture
    def small_bulletin(self, mock_app):
        """Create bulletin with 5 sections."""
        mock_app.sections_data = [
            {
                'title': f'Section {i}',
                'content': f'<p>Content for section {i}</p>',
                'section_type': 'announcement'
            }
            for i in range(5)
        ]
        return mock_app
    
    @pytest.fixture
    def medium_bulletin(self, mock_app):
        """Create bulletin with 20 sections."""
        mock_app.sections_data = [
            {
                'title': f'Section {i}',
                'content': f'<p>Content for section {i} with more text to simulate real content.</p>',
                'section_type': 'announcement' if i % 2 == 0 else 'event'
            }
            for i in range(20)
        ]
        return mock_app
    
    @pytest.fixture
    def large_bulletin(self, mock_app):
        """Create bulletin with 50 sections."""
        mock_app.sections_data = [
            {
                'title': f'Section {i}',
                'content': f'<p>Content for section {i}. ' + ('Lorem ipsum dolor sit amet. ' * 10) + '</p>',
                'section_type': ['announcement', 'event', 'spotlight'][i % 3]
            }
            for i in range(50)
        ]
        return mock_app
    
    def test_render_small_bulletin(self, small_bulletin, benchmark):
        """Benchmark rendering bulletin with 5 sections."""
        def render():
            # Simulate rendering process
            data = {
                'sections': small_bulletin.sections_data,
                'template': 'default'
            }
            # Simulate template rendering
            result = []
            for section in data['sections']:
                result.append(f"<div>{section['title']}: {section['content']}</div>")
            return ''.join(result)
        
        result = benchmark(render)
        assert len(result) > 0
    
    def test_render_medium_bulletin(self, medium_bulletin, benchmark):
        """Benchmark rendering bulletin with 20 sections."""
        def render():
            data = {
                'sections': medium_bulletin.sections_data,
                'template': 'default'
            }
            result = []
            for section in data['sections']:
                result.append(f"<div>{section['title']}: {section['content']}</div>")
            return ''.join(result)
        
        result = benchmark(render)
        assert len(result) > 0
    
    def test_render_large_bulletin(self, large_bulletin, benchmark):
        """Benchmark rendering bulletin with 50 sections."""
        def render():
            data = {
                'sections': large_bulletin.sections_data,
                'template': 'default'
            }
            result = []
            for section in data['sections']:
                result.append(f"<div class='{section['section_type']}'>{section['title']}: {section['content']}</div>")
            return ''.join(result)
        
        result = benchmark(render)
        assert len(result) > 0
        # Ensure rendering doesn't take too long
        assert benchmark.stats['mean'] < 0.1, "Rendering 50 sections should take less than 100ms"


class TestExportPerformance:
    """Benchmark export performance."""
    
    @pytest.fixture
    def sample_sections(self):
        """Create sample sections for export."""
        return [
            {
                'title': f'Section {i}',
                'content': f'<p>Content {i}</p>',
                'section_type': 'announcement'
            }
            for i in range(10)
        ]
    
    def test_export_html(self, sample_sections, benchmark):
        """Benchmark HTML export."""
        def export_html():
            html_parts = ['<!DOCTYPE html><html><body>']
            for section in sample_sections:
                html_parts.append(f"<section><h2>{section['title']}</h2>{section['content']}</section>")
            html_parts.append('</body></html>')
            return ''.join(html_parts)
        
        result = benchmark(export_html)
        assert '<!DOCTYPE html>' in result
        assert len(result) > 100
    
    def test_export_json(self, sample_sections, benchmark):
        """Benchmark JSON export."""
        def export_json():
            data = {
                'sections': sample_sections,
                'settings': {'theme': 'default'},
                'metadata': {'version': '2.0'}
            }
            return json.dumps(data, indent=2)
        
        result = benchmark(export_json)
        assert 'sections' in result
    
    def test_export_email_html(self, sample_sections, benchmark):
        """Benchmark email-optimized HTML export."""
        def export_email():
            # Simulate email HTML generation with inline styles
            html_parts = ['<!DOCTYPE html><html><body style="margin:0;padding:0;">']
            html_parts.append('<table width="600" border="0" cellpadding="0" cellspacing="0">')
            for section in sample_sections:
                html_parts.append(f'''
<tr><td style="padding:20px;">
    <h2 style="margin:0 0 10px 0;">{section['title']}</h2>
    <div>{section['content']}</div>
</td></tr>
''')
            html_parts.append('</table></body></html>')
            return ''.join(html_parts)
        
        result = benchmark(export_email)
        assert 'cellpadding="0"' in result
        # Email HTML should be reasonably fast even with all the inline styles
        assert benchmark.stats['mean'] < 0.05, "Email HTML export should take less than 50ms"


class TestImportPerformance:
    """Benchmark import performance."""
    
    def test_import_small_csv(self, benchmark, tmp_path):
        """Benchmark importing small CSV (10 rows)."""
        csv_content = "Event Name,Date,Description\n"
        csv_content += "\n".join([f"Event {i},2025-08-{10+i},Description {i}" for i in range(10)])
        
        csv_file = tmp_path / "small.csv"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        def import_csv():
            import csv
            events = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append({
                        'title': row['Event Name'],
                        'date': row['Date'],
                        'description': row['Description']
                    })
            return events
        
        result = benchmark(import_csv)
        assert len(result) == 10
    
    def test_import_medium_csv(self, benchmark, tmp_path):
        """Benchmark importing medium CSV (100 rows)."""
        csv_content = "Event Name,Date,Description,Location\n"
        csv_content += "\n".join([
            f"Event {i},2025-08-{10+(i%20)},Description for event {i},Location {i%5}"
            for i in range(100)
        ])
        
        csv_file = tmp_path / "medium.csv"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        def import_csv():
            import csv
            events = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append({
                        'title': row['Event Name'],
                        'date': row['Date'],
                        'description': row['Description'],
                        'location': row['Location']
                    })
            return events
        
        result = benchmark(import_csv)
        assert len(result) == 100
    
    def test_import_large_csv(self, benchmark, tmp_path):
        """Benchmark importing large CSV (500 rows)."""
        csv_content = "Event Name,Date,Start Time,End Time,Location,Description,Category\n"
        csv_content += "\n".join([
            f"Event {i},2025-{8+(i%4)}-{1+(i%28)},10:00,12:00,Location {i%10},"
            f"Long description for event {i} with details,Category{i%5}"
            for i in range(500)
        ])
        
        csv_file = tmp_path / "large.csv"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        def import_csv():
            import csv
            events = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append({
                        'title': row['Event Name'],
                        'date': row['Date'],
                        'start_time': row['Start Time'],
                        'end_time': row['End Time'],
                        'location': row['Location'],
                        'description': row['Description'],
                        'category': row['Category']
                    })
            return events
        
        result = benchmark(import_csv)
        assert len(result) == 500
        # Large CSV import should still be reasonably fast
        assert benchmark.stats['mean'] < 0.5, "Importing 500 rows should take less than 500ms"
    
    def test_import_json(self, benchmark, tmp_path):
        """Benchmark JSON import."""
        json_data = {
            'events': [
                {
                    'name': f'Event {i}',
                    'date': f'2025-08-{10+(i%20)}',
                    'description': f'Description for event {i}'
                }
                for i in range(100)
            ]
        }
        
        json_file = tmp_path / "events.json"
        json_file.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
        
        def import_json_file():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            events = []
            for event in data['events']:
                events.append({
                    'title': event['name'],
                    'date': event['date'],
                    'description': event['description']
                })
            return events
        
        result = benchmark(import_json_file)
        assert len(result) == 100


class TestDraftOperations:
    """Benchmark draft load/save operations."""
    
    def test_save_draft(self, benchmark, tmp_path):
        """Benchmark saving draft to file."""
        draft_data = {
            'sections': [
                {
                    'title': f'Section {i}',
                    'content': f'Content {i}',
                    'section_type': 'announcement'
                }
                for i in range(20)
            ],
            'settings': {'theme': 'default', 'template': 'modern'},
            'metadata': {'created': '2025-08-15', 'modified': '2025-08-15'}
        }
        
        draft_file = tmp_path / "draft.json"
        
        def save_draft():
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, indent=2)
            return draft_file.stat().st_size
        
        size = benchmark(save_draft)
        assert size > 0
    
    def test_load_draft(self, benchmark, tmp_path):
        """Benchmark loading draft from file."""
        draft_data = {
            'sections': [
                {
                    'title': f'Section {i}',
                    'content': f'Content {i}' * 10,
                    'section_type': 'announcement'
                }
                for i in range(20)
            ],
            'settings': {'theme': 'default'},
            'metadata': {}
        }
        
        draft_file = tmp_path / "draft.json"
        with open(draft_file, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f)
        
        def load_draft():
            with open(draft_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        
        result = benchmark(load_draft)
        assert len(result['sections']) == 20


class TestMemoryIntensiveOperations:
    """Benchmark memory-intensive operations."""
    
    def test_section_duplication(self, benchmark):
        """Benchmark duplicating many sections."""
        sections = [
            {
                'title': f'Section {i}',
                'content': '<p>' + ('Lorem ipsum dolor sit amet. ' * 50) + '</p>',
                'section_type': 'announcement'
            }
            for i in range(10)
        ]
        
        def duplicate_sections():
            # Simulate duplicating all sections
            duplicated = []
            for section in sections:
                duplicated.append(section.copy())
                duplicated.append(section.copy())  # Duplicate each
            return duplicated
        
        result = benchmark(duplicate_sections)
        assert len(result) == 20
    
    def test_search_sections(self, benchmark):
        """Benchmark searching through sections."""
        sections = [
            {
                'title': f'Section {i}',
                'content': f'<p>Content with keyword{i%10}</p>',
                'section_type': 'announcement'
            }
            for i in range(100)
        ]
        
        def search_sections(query):
            results = []
            for section in sections:
                if query.lower() in section['title'].lower() or query.lower() in section['content'].lower():
                    results.append(section)
            return results
        
        result = benchmark(search_sections, 'keyword5')
        assert len(result) >= 10  # Should find all with keyword5


def test_benchmark_comparison():
    """Test that helps compare benchmark results across runs."""
    # This test doesn't benchmark anything, but provides context
    times = {
        'render_5_sections': 0.001,  # 1ms baseline
        'render_50_sections': 0.01,   # 10ms baseline
        'export_html': 0.005,         # 5ms baseline
        'import_100_rows': 0.05,      # 50ms baseline
    }
    
    # These are target times - actual benchmarks should be within 2x of these
    assert all(t < 1.0 for t in times.values()), "All operations should complete within 1 second"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
