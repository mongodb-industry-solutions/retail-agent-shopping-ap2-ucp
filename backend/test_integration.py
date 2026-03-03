#!/usr/bin/env python3
"""
Test script to verify A2A agent integration.

This script tests that all agents start properly and are reachable.
Run this after starting the backend service to verify the integration.
"""

import asyncio
import aiohttp
import sys
import time
from typing import Dict, Any


async def test_endpoint(session: aiohttp.ClientSession, url: str, name: str) -> Dict[str, Any]:
    """Test a single endpoint and return the result."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "name": name,
                    "url": url, 
                    "status": "✅ OK",
                    "response_code": response.status,
                    "data": data
                }
            else:
                return {
                    "name": name,
                    "url": url,
                    "status": f"❌ HTTP {response.status}",
                    "response_code": response.status
                }
    except Exception as e:
        return {
            "name": name,
            "url": url, 
            "status": f"❌ ERROR: {str(e)}",
            "error": str(e)
        }


async def test_backend_integration():
    """Test the backend service and A2A agent integration."""
    print("🧪 Testing Backend Service with A2A Agent Integration")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        (f"{base_url}/", "Backend Root"),
        (f"{base_url}/health", "Backend Health"),
        (f"{base_url}/api/shopping/", "Shopping API Root"),
        (f"{base_url}/api/shopping/health", "Shopping Health"),
        (f"{base_url}/api/shopping/agents/status", "Agent Status"),
    ]
    
    async with aiohttp.ClientSession() as session:
        print("Testing endpoints...")
        
        tasks = [test_endpoint(session, url, name) for url, name in endpoints]
        results = await asyncio.gather(*tasks)
        
        print("\n📊 Test Results:")
        print("-" * 40)
        
        success_count = 0
        total_count = len(results)
        
        for result in results:
            print(f"{result['status']} {result['name']}")
            print(f"    URL: {result['url']}")
            
            if "✅" in result['status']:
                success_count += 1
                if 'data' in result:
                    # Show key information from successful responses
                    data = result['data']
                    if 'agents' in data:
                        agents = data['agents']
                        if isinstance(agents, dict) and 'running_agents' in agents:
                            print(f"    Agents: {agents['running_agents']}/{agents['total_agents']} running")
                    elif 'agents_healthy' in data:
                        print(f"    Agents Healthy: {data['agents_healthy']}")
            
            print()
        
        # Overall results
        print("=" * 60)
        if success_count == total_count:
            print("🎉 All tests passed! Backend and A2A agents are working properly.")
            return True
        else:
            print(f"⚠️  {success_count}/{total_count} tests passed.")
            print("Some services may not be running correctly.")
            return False


async def main():
    """Main test function."""
    print("Waiting 3 seconds for services to be ready...")
    time.sleep(3)
    
    try:
        success = await test_backend_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())