#!/usr/bin/env python3
"""
Test all agents by running their individual test_simple.py files in their own directories.
This ensures each agent runs with its own dependencies and environment.
"""

import os
import subprocess
import sys
from pathlib import Path

def test_agent(agent_name, test_file="test_simple.py"):
    """Test an individual agent in its directory."""
    backend_dir = Path(__file__).parent
    agent_dir = backend_dir / agent_name
    
    if not agent_dir.exists():
        print(f"  [SKIP] {agent_name}: Directory not found")
        return False
    
    test_path = agent_dir / test_file
    if not test_path.exists():
        print(f"  [SKIP] {agent_name}: No {test_file} found, skipping")
        return True  # Not a failure, just skip
    
    # Set environment for mocked lambdas
    env = os.environ.copy()
    env['MOCK_LAMBDAS'] = 'true'
    # Unset VIRTUAL_ENV to avoid conflicts with subdirectory uv projects
    env.pop('VIRTUAL_ENV', None)
    
    # Run the test with uv (with timeout to prevent hanging)
    cmd = ['uv', 'run', test_file]
    print(f"Running in {agent_dir}: {' '.join(cmd)}")
    print(f"  [TESTING] May take 15-30 seconds due to LLM calls...")
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=str(agent_dir), 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=120  # 120 second timeout (2 minutes)
        )
        success = result.returncode == 0
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] {agent_name}: Test TIMEOUT (>120s)")
        return False
    
    if success:
        print(f"  [PASS] {agent_name}: Test passed")
        if stdout and "Status Code: 200" in stdout:
            # Extract key info from successful runs
            for line in stdout.split('\n'):
                if 'Tagged:' in line or 'Success:' in line or 'Message:' in line:
                    print(f"     {line.strip()}")
    else:
        print(f"  [FAIL] {agent_name}: Test failed (exit code: {result.returncode})")
        # Show actual errors from stdout (Traceback, Exception)
        if stdout:
            error_lines = []
            lines = stdout.split('\n')
            for i, line in enumerate(lines):
                if 'Traceback' in line or 'Error:' in line or 'Exception:' in line:
                    # Show traceback context
                    error_lines.extend(lines[i:min(i+5, len(lines))])
                    break
            if error_lines:
                for line in error_lines[:5]:
                    if line.strip():
                        print(f"     {line.strip()[:150]}")
        # Only show stderr if there are actual errors (not just INFO logs)
        if stderr and result.returncode != 0:
            error_lines = [l for l in stderr.split('\n') 
                          if l.strip() and 'INFO' not in l and 'LiteLLM completion()' not in l]
            for line in error_lines[:3]:
                if line.strip():
                    print(f"     stderr: {line.strip()[:150]}")
    
    return success

def main():
    """Run all agent tests."""
    print("="*60)
    print("TESTING ALL AGENTS")
    print("Running individual test_simple.py in each agent directory")
    print("="*60)
    
    # List of agents to test
    agents = [
        'tagger',
        'reporter', 
        'charter',
        'retirement',
        'planner'
    ]
    
    results = {}
    
    for agent in agents:
        print(f"\n{agent.upper()} Agent:")
        results[agent] = test_agent(agent)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    failed = sum(1 for r in results.values() if not r)
    
    print(f"Passed: {passed}/{len(agents)}")
    print(f"Failed: {failed}/{len(agents)}")
    
    if failed > 0:
        print("\nFailed agents:")
        for agent, success in results.items():
            if not success:
                print(f"  - {agent}")
    
    print("="*60)
    
    if failed > 0:
        print("\n[WARNING] SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        sys.exit(0)

if __name__ == "__main__":
    main()