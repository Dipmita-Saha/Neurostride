#!/usr/bin/env python3
"""
Test script to verify NeuroStride backend-frontend connection
"""
import requests
import json
import base64
import time
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (640, 480), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    return base64.b64encode(img_data).decode('utf-8')

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✓ Backend health check passed")
            print(f"  Status: {health_data.get('status')}")
            print(f"  Model loaded: {health_data.get('model_loaded')}")
            return True
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend connection failed: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze_frame endpoint"""
    try:
        test_image = create_test_image()
        payload = {
            "image": f"data:image/png;base64,{test_image}",
            "session_id": "test_session",
            "force": True
        }
        
        response = requests.post(
            'http://localhost:5000/analyze_frame',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis endpoint test passed")
            print(f"  Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"✗ Analysis endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Analysis endpoint connection failed: {e}")
        return False

def test_frontend_server():
    """Test if frontend server is accessible"""
    try:
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code == 200:
            print("✓ Frontend server accessible")
            return True
        else:
            print(f"✗ Frontend server returned: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Frontend server connection failed: {e}")
        return False

def main():
    print("NeuroStride Connection Test")
    print("=" * 30)
    
    # Test backend
    print("\n1. Testing Backend Server...")
    backend_ok = test_backend_health()
    
    if backend_ok:
        print("\n2. Testing Analysis Endpoint...")
        analyze_ok = test_analyze_endpoint()
    else:
        analyze_ok = False
        print("\n2. Skipping analysis test (backend not available)")
    
    # Test frontend
    print("\n3. Testing Frontend Server...")
    frontend_ok = test_frontend_server()
    
    # Summary
    print("\n" + "=" * 30)
    print("Test Summary:")
    print(f"Backend Health: {'✓' if backend_ok else '✗'}")
    print(f"Analysis API: {'✓' if analyze_ok else '✗'}")
    print(f"Frontend Server: {'✓' if frontend_ok else '✗'}")
    
    if backend_ok and analyze_ok and frontend_ok:
        print("\n🎉 All tests passed! NeuroStride is ready to use.")
        print("Open http://localhost:8080 in your browser.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        if not backend_ok:
            print("   - Make sure to run 'python app.py' in the backend directory")
        if not frontend_ok:
            print("   - Make sure to run 'python serve.py' in the frontend directory")

if __name__ == "__main__":
    main()