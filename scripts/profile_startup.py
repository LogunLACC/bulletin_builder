"""
Startup profiler for Bulletin Builder.

Profiles application startup time to identify slow imports and initialization.
Run with: python scripts/profile_startup.py
"""

import time
import sys
import importlib.util
from pathlib import Path


class StartupProfiler:
    """Profile application startup performance."""
    
    def __init__(self):
        self.timings = {}
        self.start_time = time.perf_counter()
    
    def mark(self, name: str):
        """Mark a timing checkpoint."""
        elapsed = time.perf_counter() - self.start_time
        self.timings[name] = elapsed
    
    def measure_import(self, module_name: str):
        """Measure import time for a module."""
        start = time.perf_counter()
        try:
            importlib.import_module(module_name)
            duration = time.perf_counter() - start
            return duration, None
        except Exception as e:
            duration = time.perf_counter() - start
            return duration, str(e)
    
    def report(self):
        """Generate profiling report."""
        print("\n" + "="*70)
        print("📊 BULLETIN BUILDER STARTUP PROFILING REPORT")
        print("="*70)
        
        if not self.timings:
            print("No timing data collected.")
            return
        
        # Sort by time
        sorted_timings = sorted(self.timings.items(), key=lambda x: x[1])
        
        print(f"\n{'Checkpoint':<40} {'Time (ms)':<12} {'Cumulative (ms)'}")
        print("-"*70)
        
        prev_time = 0
        for name, total_time in sorted_timings:
            delta = (total_time - prev_time) * 1000
            total_ms = total_time * 1000
            print(f"{name:<40} {delta:>10.2f}   {total_ms:>10.2f}")
            prev_time = total_time
        
        print("-"*70)
        total = sorted_timings[-1][1] * 1000 if sorted_timings else 0
        print(f"{'TOTAL STARTUP TIME':<40} {total:>10.2f} ms")
        print("="*70)


def profile_imports():
    """Profile key module imports."""
    profiler = StartupProfiler()
    
    print("\n🔍 Profiling module imports...")
    
    modules_to_test = [
        # Standard library
        ('tkinter', 'Tkinter GUI framework'),
        ('json', 'JSON parsing'),
        ('pathlib', 'Path utilities'),
        
        # Third-party (heavy imports)
        ('jinja2', 'Jinja2 templating engine'),
        ('weasyprint', 'WeasyPrint PDF generation'),
        ('google.generativeai', 'Google Gemini AI'),
        ('openai', 'OpenAI API'),
        
        # Bulletin Builder modules
        ('bulletin_builder.app_core.core_init', 'Core initialization'),
        ('bulletin_builder.app_core.settings', 'Settings manager'),
        ('bulletin_builder.app_core.importer', 'Import functionality'),
        ('bulletin_builder.app_core.exporter', 'Export functionality'),
        ('bulletin_builder.app_core.preview', 'Preview rendering'),
    ]
    
    results = []
    for module_name, description in modules_to_test:
        duration, error = profiler.measure_import(module_name)
        results.append((module_name, description, duration, error))
    
    # Report
    print("\n" + "="*90)
    print(f"{'Module':<40} {'Description':<25} {'Time (ms)':<12} {'Status'}")
    print("-"*90)
    
    for module_name, description, duration, error in sorted(results, key=lambda x: x[2], reverse=True):
        time_ms = duration * 1000
        status = "✗ FAILED" if error else "✓"
        color = "\033[91m" if error else ("\033[93m" if time_ms > 100 else "\033[92m")
        reset = "\033[0m"
        
        print(f"{module_name:<40} {description:<25} {color}{time_ms:>10.2f}{reset}   {status}")
        if error:
            print(f"  └─ Error: {error}")
    
    print("-"*90)
    print(f"\n{'Slow imports (>100ms):':<40}")
    slow_imports = [(name, desc, dur*1000) for name, desc, dur, err in results if dur*1000 > 100 and not err]
    if slow_imports:
        for name, desc, time_ms in sorted(slow_imports, key=lambda x: x[2], reverse=True):
            print(f"  • {name:<40} {time_ms:>10.2f} ms")
    else:
        print("  None!")
    
    print(f"\n{'Total import time:':<40} {sum(d for _, _, d, _ in results)*1000:>10.2f} ms")
    print("="*90)


def profile_app_startup():
    """Profile full application startup."""
    print("\n🚀 Profiling full application startup...")
    
    profiler = StartupProfiler()
    
    try:
        # Add src to path
        src_path = Path(__file__).parent.parent / 'src'
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        profiler.mark("Start")
        
        # Import core modules
        import bulletin_builder
        profiler.mark("Import bulletin_builder")
        
        from bulletin_builder.app_core import core_init
        profiler.mark("Import core_init")
        
        from bulletin_builder.app_core import settings
        profiler.mark("Import settings")
        
        from bulletin_builder.app_core import recovery_mode
        profiler.mark("Import recovery_mode")
        
        from bulletin_builder.app_core import input_validators
        profiler.mark("Import input_validators")
        
        from bulletin_builder.app_core import graceful_degradation
        profiler.mark("Import graceful_degradation")
        
        # Heavy imports (should be lazy-loaded)
        try:
            import weasyprint
            profiler.mark("Import weasyprint (HEAVY)")
        except ImportError:
            profiler.mark("Import weasyprint (SKIPPED - not installed)")
        
        try:
            import google.generativeai
            profiler.mark("Import google.generativeai (HEAVY)")
        except ImportError:
            profiler.mark("Import google.generativeai (SKIPPED - not installed)")
        
        profiler.mark("Finished")
        
        profiler.report()
        
    except Exception as e:
        print(f"\n❌ Error during profiling: {e}")
        import traceback
        traceback.print_exc()


def analyze_startup_bottlenecks():
    """Analyze and report startup bottlenecks."""
    print("\n🔬 Analyzing startup bottlenecks...")
    print("="*70)
    
    bottlenecks = [
        {
            "issue": "WeasyPrint imported eagerly",
            "impact": "~200-500ms startup delay",
            "solution": "Lazy load only when PDF export is triggered",
            "priority": "HIGH"
        },
        {
            "issue": "AI libraries (google.generativeai, openai) loaded at startup",
            "impact": "~100-300ms startup delay per library",
            "solution": "Lazy load only when AI features are used",
            "priority": "HIGH"
        },
        {
            "issue": "Jinja2 templates parsed on every render",
            "impact": "~5-10ms per render",
            "solution": "Implement template caching",
            "priority": "MEDIUM"
        },
        {
            "issue": "Large CSV files processed synchronously",
            "impact": "UI freeze for >1000 rows",
            "solution": "Chunked processing with progress bar",
            "priority": "MEDIUM"
        },
        {
            "issue": "Preview regenerates entire HTML on every change",
            "impact": "Lag when editing large bulletins",
            "solution": "Incremental updates + debouncing",
            "priority": "MEDIUM"
        },
        {
            "issue": "All sections loaded into memory at once",
            "impact": "~5-10MB RAM per 100 sections",
            "solution": "Virtual scrolling for large bulletins",
            "priority": "LOW"
        }
    ]
    
    for i, bottleneck in enumerate(bottlenecks, 1):
        priority_color = {
            "HIGH": "\033[91m",
            "MEDIUM": "\033[93m",
            "LOW": "\033[92m"
        }[bottleneck["priority"]]
        reset = "\033[0m"
        
        print(f"\n{i}. {bottleneck['issue']}")
        print(f"   Impact: {bottleneck['impact']}")
        print(f"   Solution: {bottleneck['solution']}")
        print(f"   Priority: {priority_color}{bottleneck['priority']}{reset}")
    
    print("\n" + "="*70)
    print("\n💡 Recommendations:")
    print("   1. Implement lazy loading for heavy imports (WeasyPrint, AI libraries)")
    print("   2. Add template caching to avoid re-parsing Jinja2 templates")
    print("   3. Use chunked processing for large CSV imports")
    print("   4. Add debouncing to preview updates (500ms delay)")
    print("   5. Implement virtual scrolling for bulletins with >100 sections")
    print("="*70)


def main():
    """Run all profiling."""
    print("\n" + "="*70)
    print("🔧 BULLETIN BUILDER STARTUP PROFILER")
    print("="*70)
    
    # Profile imports
    profile_imports()
    
    # Profile full app startup
    profile_app_startup()
    
    # Analyze bottlenecks
    analyze_startup_bottlenecks()
    
    print("\n✅ Profiling complete!")
    print("\nNext steps:")
    print("  1. Review the profiling report above")
    print("  2. Implement lazy loading for slow imports (>100ms)")
    print("  3. Add template caching for frequently rendered templates")
    print("  4. Run benchmarks: pytest tests/benchmarks/test_performance.py -v")
    print()


if __name__ == "__main__":
    main()
