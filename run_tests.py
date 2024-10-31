#!/usr/bin/env python
import unittest
import sys
import os
from datetime import datetime
import coverage

def setup_test_environment():
    """Setup the test environment and paths"""
    # Get absolute paths
    project_root = os.path.abspath(os.path.dirname(__file__))
    server_dir = os.path.join(project_root, 'server')
    
    # Add paths to Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)
    
    # Ensure the test results directory exists
    results_dir = os.path.join(project_root, 'test_results')
    os.makedirs(results_dir, exist_ok=True)
    
    return project_root, server_dir, results_dir

def discover_tests(loader, start_dir):
    """Discover tests in a directory"""
    try:
        # Make the start_dir relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(start_dir)))
        relative_dir = os.path.relpath(start_dir, project_root)
        
        # Convert path to module notation
        module_path = relative_dir.replace(os.sep, '.')
        try:
            __import__(module_path)
        except ImportError as e:
            print(f"Warning: Could not import {module_path}: {e}")
        
        return loader.discover(start_dir, pattern='test_*.py')
    except Exception as e:
        print(f"Error discovering tests in {start_dir}: {str(e)}")
        return unittest.TestSuite()

class TeeStream:
    """Stream that writes to multiple streams"""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()

def run_tests(verbosity=2):
    """Run the test suite with coverage reporting"""
    project_root, server_dir, results_dir = setup_test_environment()
    
    # Initialize coverage
    cov = coverage.Coverage(
        branch=True,
        source=[server_dir],
        omit=[
            '*/__init__.py',
            '*/tests/*',
            '*/migrations/*',
            '*/.venv/*'
        ]
    )
    
    try:
        cov.start()

        # Create test loader
        loader = unittest.TestLoader()
        
        # Collect all test suites
        suite = unittest.TestSuite()
        
        # Add tests from each test directory
        test_dirs = [
            ('models', os.path.join(project_root, 'tests', 'models')),
            ('repositories', os.path.join(project_root, 'tests', 'repositories')),
            ('services', os.path.join(project_root, 'tests', 'services'))
        ]
        
        print("\nDiscovering tests...")
        total_tests = 0
        test_counts = {}
        
        for test_type, test_dir in test_dirs:
            if os.path.exists(test_dir):
                print(f"Looking for {test_type} tests in: {test_dir}")
                tests = discover_tests(loader, test_dir)
                suite.addTests(tests)
                
                # Count tests in this category
                test_count = tests.countTestCases()
                test_counts[test_type] = test_count
                total_tests += test_count
            else:
                print(f"Warning: Test directory not found: {test_dir}")
        
        # Run the tests
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(results_dir, f'test_report_{timestamp}.txt')
        
        print(f"\nRunning {total_tests} tests...")
        
        with open(report_file, 'w') as f:
            # Create a stream that writes to both file and console
            tee = TeeStream(f, sys.stdout)
            runner = unittest.TextTestRunner(
                stream=tee,
                verbosity=verbosity,
                descriptions=True
            )
            result = runner.run(suite)
            
            # Write summary
            summary = "\nTest Execution Report\n"
            summary += "===================\n\n"
            summary += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += f"Tests Run: {result.testsRun}\n"
            summary += f"Failures: {len(result.failures)}\n"
            summary += f"Errors: {len(result.errors)}\n"
            summary += f"Skipped: {len(result.skipped)}\n\n"
            
            # Add test category summary
            summary += "Tests by Category:\n"
            summary += "-----------------\n"
            for category, count in sorted(test_counts.items()):
                summary += f"{category}: {count} test(s)\n"
            summary += f"Total: {total_tests} test(s)\n\n"
            
            if result.failures:
                summary += "\nFailures:\n"
                summary += "---------\n"
                for failure in result.failures:
                    summary += f"\n{failure[0]}\n"
                    summary += f"{failure[1]}\n"
            
            if result.errors:
                summary += "\nErrors:\n"
                summary += "-------\n"
                for error in result.errors:
                    summary += f"\n{error[0]}\n"
                    summary += f"{error[1]}\n"
            
            tee.write(summary)
        
        # Generate coverage reports
        cov.stop()
        cov.save()
        
        coverage_file = os.path.join(results_dir, f'coverage_report_{timestamp}.txt')
        with open(coverage_file, 'w') as f:
            cov.report(file=f)
        
        # Generate HTML coverage report
        html_dir = os.path.join(results_dir, f'coverage_html_{timestamp}')
        cov.html_report(directory=html_dir)
        
        print(f"\nTest report generated: {report_file}")
        print(f"Coverage report generated: {coverage_file}")
        print(f"HTML coverage report: {html_dir}/index.html")
        
        return not result.wasSuccessful()
        
    except Exception as e:
        print(f"Error running tests: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    try:
        exit_code = run_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError in test execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)