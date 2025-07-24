"""
Comprehensive system integration tests
Tests the autonomous AI agent system end-to-end
"""

import pytest
import asyncio
import requests
import json
from datetime import datetime, timedelta

# Test configuration
BACKEND_URL = "http://127.0.0.1:8001"
TEST_TIMEOUT = 300  # 5 minutes

class TestAutonomousSystem:
    """Test suite for the autonomous AI agent system"""
    
    def setup_method(self):
        """Setup before each test"""
        # Check if backend is running
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            assert response.status_code == 200
        except:
            pytest.skip("Backend not running")
    
    def test_health_check(self):
        """Test basic health check"""
        response = requests.get(f"{BACKEND_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "agents_available" in data
        assert "tools_available" in data
    
    def test_chat_completions_basic(self):
        """Test basic chat completions API"""
        payload = {
            "messages": [
                {"role": "user", "content": "Hello, can you help me?"}
            ]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert data["choices"][0]["message"]["role"] == "assistant"
    
    def test_models_endpoint(self):
        """Test models listing endpoint"""
        response = requests.get(f"{BACKEND_URL}/v1/models")
        
        # This might fail if Ollama is not running, which is expected
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
        else:
            # Expected to fail without Ollama
            assert response.status_code == 500
    
    def test_task_submission(self):
        """Test task submission and tracking"""
        # Submit a simple task
        task_payload = {
            "objective": "Create a simple Python calculator script",
            "priority": "normal"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/v1/tasks/submit",
            json=task_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "submitted"
        
        session_id = data["session_id"]
        
        # Check task status
        status_response = requests.get(f"{BACKEND_URL}/v1/tasks/{session_id}/status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["session_id"] == session_id
        assert "status" in status_data
        assert "progress" in status_data
    
    def test_enterprise_tools_endpoints(self):
        """Test enterprise tools endpoints"""
        # Test write-file endpoint
        write_payload = {
            "file_path": "test_file.txt",
            "content": "Hello, World!"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/enterprise/write-file",
            params=write_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success", False)
        
        # Test run-shell endpoint (simple command)
        shell_payload = {
            "command": "echo 'test command'"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/enterprise/run-shell",
            params=shell_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "stdout" in data
    
    def test_quant_endpoints(self):
        """Test quantitative trading endpoints"""
        # Test strategies listing
        response = requests.get(f"{BACKEND_URL}/api/quant/strategies")
        assert response.status_code == 200
        
        data = response.json()
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
        
        # Test backtest endpoint (if strategies available)
        if data["strategies"]:
            strategy_name = data["strategies"][0]
            backtest_payload = {
                "strategy_name": strategy_name,
                "symbol": "TEST",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/quant/backtest",
                params=backtest_payload
            )
            
            assert response.status_code == 200
            backtest_data = response.json()
            assert "success" in backtest_data
    
    def test_screenshot_api(self):
        """Test screenshot API endpoints"""
        # Test screenshot endpoint
        screenshot_payload = {
            "analyze": True,
            "ocr": True,
            "store_in_memory": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/screenshot/screenshot",
            json=screenshot_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "preview" in data
        
        # Test queue endpoint
        response = requests.get(f"{BACKEND_URL}/api/screenshot/queue")
        assert response.status_code == 200
        
        queue_data = response.json()
        assert "queue" in queue_data
        assert "total_count" in queue_data
    
    def test_tools_api(self):
        """Test automation tools API"""
        # Test screen size endpoint
        response = requests.get(f"{BACKEND_URL}/api/tools/screen-size")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success", False)
        assert "width" in data
        assert "height" in data
        
        # Test clipboard read endpoint
        response = requests.get(f"{BACKEND_URL}/api/tools/clipboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success", False)
        assert "text" in data
    
    def test_complex_task_flow(self):
        """Test a complex task flow end-to-end"""
        # This test simulates a real workflow
        
        # 1. Submit a complex task
        task_payload = {
            "objective": "Create a simple web application with a React frontend and Python backend",
            "priority": "high"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/v1/tasks/submit",
            json=task_payload
        )
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # 2. Monitor task progress
        max_wait_time = 60  # 1 minute for this test
        start_time = datetime.now()
        
        while datetime.now() - start_time < timedelta(seconds=max_wait_time):
            status_response = requests.get(f"{BACKEND_URL}/v1/tasks/{session_id}/status")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                # Check if task is making progress
                assert "progress" in status_data
                assert status_data["progress"] >= 0
                
                # If completed or failed, break
                if status_data.get("status") in ["completed", "failed"]:
                    break
            
            # Wait before next check
            import time
            time.sleep(2)
        
        # 3. Verify final status
        final_response = requests.get(f"{BACKEND_URL}/v1/tasks/{session_id}/status")
        assert final_response.status_code == 200
        
        final_data = final_response.json()
        # The task might not complete in the test timeframe, which is okay
        assert final_data["session_id"] == session_id
    
    def test_error_handling(self):
        """Test error handling and recovery"""
        # Test invalid task submission
        invalid_payload = {
            "objective": "",  # Empty objective
        }
        
        response = requests.post(
            f"{BACKEND_URL}/v1/tasks/submit",
            json=invalid_payload
        )
        
        # Should handle gracefully (might accept or reject)
        assert response.status_code in [200, 400, 422]
        
        # Test invalid session ID
        response = requests.get(f"{BACKEND_URL}/v1/tasks/invalid_session_id/status")
        assert response.status_code == 404
        
        # Test malformed requests
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            json={"invalid": "format"}
        )
        assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])