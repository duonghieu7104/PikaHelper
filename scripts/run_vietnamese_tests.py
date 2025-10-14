#!/usr/bin/env python3
"""
Master script to run all Vietnamese text processing tests
"""

import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and return success status"""
    print(f"\n{'='*60}")
    print(f"🚀 Running: {description}")
    print(f"📁 Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ Script {script_name} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Run all Vietnamese text processing tests"""
    
    print("🇻🇳 Vietnamese Text Processing Test Suite")
    print("=" * 60)
    print("This script will test:")
    print("1. Vietnamese embedding service")
    print("2. Vietnamese text preprocessing libraries")
    print("3. Complete pipeline from text to embedding")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("scripts"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # List of tests to run
    tests = [
        ("scripts/quick_vietnamese_test.py", "Quick Vietnamese Embedding Test"),
        ("scripts/test_vi_stag.py", "Vietnamese Text Processing Libraries Test"),
        ("scripts/test_vietnamese_embedding.py", "Full Vietnamese Embedding Pipeline Test")
    ]
    
    results = {}
    
    for script_name, description in tests:
        if os.path.exists(script_name):
            success = run_script(script_name, description)
            results[script_name] = success
        else:
            print(f"⚠️  Script not found: {script_name}")
            results[script_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for script_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {os.path.basename(script_name)}: {status}")
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Vietnamese processing is working correctly.")
        return True
    elif passed_tests > 0:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Check the output above for details.")
        return False
    else:
        print("\n❌ All tests failed. Check your setup and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
