# run_tests.py
import unittest
import sys
import os
from datetime import datetime
import coverage

def setup_test_environment():
    """Setup the test environment and paths"""
    # Get absolute paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add paths to system path
    sys.path.insert(0, current_dir)  # Add project root
    sys.path.insert(0, os.path.join(current_dir, 'server'))  # Add server root
    sys.path.insert(0, os.path.join(current_dir, 'server/utils'))  # Add utils directory
    
    # Create test results directory
    results_dir = os.path.join(current_dir, 'test_results')
    os.makedirs(results_dir, exist_ok=True)
    
    return current_dir, results_dir


def discover_tests(loader, test_dir):
    """Discover tests in a directory"""
    if not os.path.exists(test_dir):
        print(f"Warning: Test directory not found: {test_dir}")
        return unittest.TestSuite()
        
    try:
        return loader.discover(start_dir=test_dir, pattern='test_*.py')
    except Exception as e:
        print(f"Error discovering tests in {test_dir}: {str(e)}")
        return unittest.TestSuite()

def run_tests():
    """Run the test suite"""
    project_root, results_dir = setup_test_environment()
    
    # Initialize coverage
    cov = coverage.Coverage(
        branch=True,
        source=[os.path.join(project_root, 'server')],
        omit=[
            '*/__init__.py',
            '*/tests/*',
            '*/.venv/*'
        ]
    )
    
    try:
        cov.start()
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Define test directories
        test_dir = os.path.join(project_root, 'tests')
        services_dir = os.path.join(test_dir, 'services')
        
        # Add tests
        loader = unittest.TestLoader()
        services_tests = discover_tests(loader, services_dir)
        suite.addTests(services_tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage and save report
        cov.stop()
        cov.save()
        
        # Generate coverage reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        coverage_file = os.path.join(results_dir, f'coverage_report_{timestamp}.txt')
        
        with open(coverage_file, 'w') as f:
            cov.report(file=f)
        
        # Generate HTML coverage report
        html_dir = os.path.join(results_dir, f'coverage_html_{timestamp}')
        cov.html_report(directory=html_dir)
        
        return not result.wasSuccessful()
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())