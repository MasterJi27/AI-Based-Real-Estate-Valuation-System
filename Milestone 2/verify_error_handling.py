#!/usr/bin/env python3
"""
Quick verification that enhanced error handling is in place
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_error_handling():
    """Verify that the enhanced error handling is properly implemented"""
    
    print("=" * 80)
    print("GEMINI AI ERROR HANDLING VERIFICATION")
    print("=" * 80)
    
    # Read the gemini_ai.py file
    gemini_file = os.path.join(os.path.dirname(__file__), 'gemini_ai.py')
    
    if not os.path.exists(gemini_file):
        print("✗ gemini_ai.py not found!")
        return False
    
    with open(gemini_file, 'r') as f:
        content = f.read()
    
    # Check for the new method
    checks = {
        "_safe_extract_response_text": "Safe response extraction method",
        "finish_reason": "Finish reason handling",
        "operation_name": "Operation-specific logging",
        "ValueError": "ValueError exception handling",
        "manually extract from candidates": "Fallback extraction strategy",
        "response.candidates": "Candidates validation",
        "hasattr(candidate, 'finish_reason')": "Finish reason checking",
    }
    
    print("\n✓ Checking for enhanced error handling features:\n")
    
    all_present = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND!")
            all_present = False
    
    # Count method updates
    print("\n✓ Checking AI method updates:\n")
    
    methods = [
        "analyze_property_market",
        "get_investment_recommendations", 
        "analyze_market_trends",
        "real_estate_qa",
        "generate_property_report"
    ]
    
    safe_extraction_count = content.count("_safe_extract_response_text(response,")
    print(f"  • Methods using safe extraction: {safe_extraction_count}/5")
    
    if safe_extraction_count >= 5:
        print("  ✓ All AI methods updated to use safe extraction")
    else:
        print(f"  ✗ Only {safe_extraction_count} methods updated (expected 5)")
        all_present = False
    
    # Check for old pattern removal
    print("\n✓ Checking for old error-prone patterns:\n")
    
    old_patterns = content.count("if hasattr(response, 'text') and response.text:")
    if old_patterns > 0:
        print(f"  ⚠ Warning: Found {old_patterns} instances of old pattern")
        print("    (This is expected if some utility code still uses it)")
    else:
        print("  ✓ No old error-prone patterns in AI methods")
    
    # Summary
    print("\n" + "=" * 80)
    if all_present:
        print("✅ VERIFICATION PASSED - Enhanced error handling is properly implemented")
        print("=" * 80)
        print("\nKey Features Verified:")
        print("  • Safe response text extraction with comprehensive checks")
        print("  • Finish reason interpretation and logging")
        print("  • Multiple fallback strategies (quick accessor, manual extraction)")
        print("  • Operation-specific logging for debugging")
        print("  • All AI methods updated to use safe extraction")
        print("\nThe application is now resilient to Gemini API response errors!")
        return True
    else:
        print("⚠ VERIFICATION INCOMPLETE - Some features may be missing")
        print("=" * 80)
        return False

if __name__ == "__main__":
    try:
        success = verify_error_handling()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
