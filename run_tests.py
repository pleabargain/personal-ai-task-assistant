import subprocess
import os
import sys
from datetime import datetime

def run_tests():
    """Run pytest with coverage and generate reports."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join('logs', 'test_runs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file for test output
    log_file = os.path.join(logs_dir, f'test_run_{timestamp}.log')
    
    try:
        # Run pytest with coverage
        print(f"Starting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Test output will be saved to:", log_file)
        
        with open(log_file, 'w') as f:
            f.write(f"Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Run pytest with coverage
            result = subprocess.run(
                [
                    'pytest',
                    '--cov=src',
                    '--cov-report=term-missing',
                    '--cov-report=html',
                    '--cov-branch',
                    '--verbose',
                    '-s'
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Write test output to log file
            f.write("=== Test Output ===\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n=== Errors ===\n")
                f.write(result.stderr)
            
            f.write(f"\nTest Run Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Print results to console
        print("\nTest Results:")
        print(result.stdout)
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
        
        # Check if tests passed
        if result.returncode != 0:
            print("\nTests failed! Check the log file for details:", log_file)
            sys.exit(1)
        else:
            print("\nAll tests passed successfully!")
            print("Coverage report generated in htmlcov/index.html")
            print("Detailed test log saved to:", log_file)
            
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        with open(log_file, 'a') as f:
            f.write(f"\n\nError running tests: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_tests()
