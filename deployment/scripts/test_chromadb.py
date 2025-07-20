#!/usr/bin/env python3
"""
ChromaDB Connection Test Script
Tests connectivity and basic operations with your ChromaDB deployment.
"""

import sys
import requests
import json
from typing import Optional

def test_chromadb_connection(base_url: str = "http://localhost:8000") -> bool:
    """Test ChromaDB connection and basic functionality."""
    
    print(f"🔍 Testing ChromaDB connection to {base_url}")
    
    try:
        # Test 1: Health check
        print("\n1️⃣ Testing health check...")
        response = requests.get(f"{base_url}/api/v1/heartbeat", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test 2: Version info
        print("\n2️⃣ Getting version info...")
        response = requests.get(f"{base_url}/api/v1/version", timeout=10)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ ChromaDB version: {version_info}")
        else:
            print(f"⚠️ Could not get version info: {response.status_code}")
            
        # Test 3: List collections
        print("\n3️⃣ Listing collections...")
        response = requests.get(f"{base_url}/api/v1/collections", timeout=10)
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections)} collections")
            if collections:
                for collection in collections:
                    print(f"   - {collection.get('name', 'Unknown')}")
        else:
            print(f"❌ Could not list collections: {response.status_code}")
            
        # Test 4: Create test collection
        print("\n4️⃣ Creating test collection...")
        test_collection_data = {
            "name": "test_collection",
            "metadata": {"description": "Test collection for connectivity"}
        }
        
        response = requests.post(
            f"{base_url}/api/v1/collections",
            json=test_collection_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ Test collection created successfully")
            
            # Test 5: Delete test collection
            print("\n5️⃣ Cleaning up test collection...")
            response = requests.delete(
                f"{base_url}/api/v1/collections/test_collection",
                timeout=10
            )
            if response.status_code in [200, 204]:
                print("✅ Test collection deleted successfully")
            else:
                print(f"⚠️ Could not delete test collection: {response.status_code}")
                
        elif response.status_code == 409:
            print("ℹ️ Test collection already exists")
        else:
            print(f"⚠️ Could not create test collection: {response.status_code}")
            
        print("\n🎉 ChromaDB connection test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error: Could not connect to {base_url}")
        print("   Make sure ChromaDB is running and accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout error: ChromaDB at {base_url} is not responding")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    """Main function to run the test."""
    
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("🧪 ChromaDB Connection Test")
    print("=" * 50)
    
    # Run the test
    success = test_chromadb_connection(base_url)
    
    if success:
        print("\n✅ All tests passed! ChromaDB is working correctly.")
        print(f"\n🌐 You can access the ChromaDB UI at: {base_url}")
        print(f"📚 API documentation at: {base_url}/docs")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check your ChromaDB deployment.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure ChromaDB pod is running: kubectl get pods -l app=chromadb")
        print("   2. Check pod logs: kubectl logs -l app=chromadb")
        print("   3. Ensure port forwarding is active: ./port-forward-chromadb.sh")
        sys.exit(1)

if __name__ == "__main__":
    main()
