#!/usr/bin/env python3
"""
Quick test to verify agent import paths are working.
This script tests that the agents can be imported without module errors.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path.cwd()))

def test_agent_imports():
    """Test that all agent modules can be imported successfully."""
    print("🧪 Testing agent module imports...")
    
    try:
        # Test merchant agent
        print("  Testing merchant_agent import...", end=" ")
        from agents.roles.merchant_agent.agent_executor import MerchantAgentExecutor
        print("✅")
        
        # Test credentials provider agent  
        print("  Testing credentials_provider_agent import...", end=" ")
        from agents.roles.credentials_provider_agent.agent_executor import CredentialsProviderExecutor
        print("✅")
        
        # Test payment processor agent
        print("  Testing merchant_payment_processor_agent import...", end=" ")
        from agents.roles.merchant_payment_processor_agent.agent_executor import PaymentProcessorExecutor
        print("✅")
        
        # Test auditor agent
        print("  Testing auditor_agent import...", end=" ")
        from agents.roles.auditor_agent.agent import root_agent
        print("✅")
        
        # Test common server module
        print("  Testing common server import...", end=" ")
        from agents.common import server
        print("✅")
        
        print("\n🎉 All agent imports successful! Module paths are correct.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_agent_imports()
    sys.exit(0 if success else 1)