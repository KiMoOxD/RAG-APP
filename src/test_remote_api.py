"""
RAG Application Remote Test Suite
Tests the deployed Railway API: Upload → Process → Index → Search → Answer
"""
import requests
import json
import time
import sys

# Railway deployment URL
BASE_URL = "https://rag-app-production-e4be.up.railway.app/api/v1"
PROJECT_ID = "remotetestproject"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_divider(title):
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_health():
    """Test health endpoint"""
    print_divider("Step 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_welcome():
    """Test welcome endpoint"""
    print_divider("Step 2: Welcome Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_upload():
    """Test file upload"""
    print_divider("Step 3: Upload File")
    
    # Create a test document
    test_content = """
    Machine Learning and Artificial Intelligence

    Machine Learning (ML) is a subset of Artificial Intelligence (AI) that enables 
    systems to learn and improve from experience without being explicitly programmed.
    
    Key concepts:
    - Supervised Learning: Learning from labeled data
    - Unsupervised Learning: Finding patterns in unlabeled data
    - Deep Learning: Neural networks with multiple layers
    - Natural Language Processing: Understanding human language
    
    AI encompasses a broader range of technologies including robotics, expert systems,
    and machine learning. The goal of AI is to create intelligent machines that can
    perform tasks that typically require human intelligence.
    
    Applications include:
    - Image recognition
    - Speech recognition
    - Recommendation systems
    - Autonomous vehicles
    - Medical diagnosis
    """
    
    try:
        files = {"file": ("test_remote.txt", test_content.encode(), "text/plain")}
        response = requests.post(
            f"{BASE_URL}/data/upload/{PROJECT_ID}",
            files=files,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200, result.get("FileName")
    except Exception as e:
        print_error(f"Error: {e}")
        return False, None

def test_process():
    """Test file processing"""
    print_divider("Step 4: Process File (Chunking)")
    payload = {
        "chunk_size": 200,
        "overlap": 20,
        "do_reset": 1
    }
    try:
        response = requests.post(
            f"{BASE_URL}/data/process/{PROJECT_ID}",
            json=payload,
            timeout=120
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_index():
    """Test indexing into vector DB"""
    print_divider("Step 5: Index into Vector DB (Qdrant Cloud)")
    payload = {"do_reset": 1}
    try:
        response = requests.post(
            f"{BASE_URL}/nlp/index/push/{PROJECT_ID}",
            json=payload,
            timeout=120
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_index_info():
    """Test getting index info"""
    print_divider("Step 6: Get Index Info")
    try:
        response = requests.get(
            f"{BASE_URL}/nlp/index/info/{PROJECT_ID}",
            timeout=30
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_search():
    """Test vector search"""
    print_divider("Step 7: Semantic Search")
    payload = {
        "text": "What is machine learning?",
        "limit": 3
    }
    try:
        response = requests.post(
            f"{BASE_URL}/nlp/index/search/{PROJECT_ID}",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if "results" in result:
            print(f"Found {len(result['results'])} results:")
            for i, r in enumerate(result['results'], 1):
                score = r.get('score', 'N/A')
                text = r.get('text', '')[:150]
                print(f"\n  Result {i} (score: {score}):")
                print(f"  {text}...")
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_answer():
    """Test RAG question answering"""
    print_divider("Step 8: RAG Answer (OpenRouter LLM)")
    payload = {
        "text": "What is the difference between AI and Machine Learning?",
        "limit": 3
    }
    
    print(f"Question: {payload['text']}")
    print("\nGenerating answer (this may take a moment)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/nlp/index/answer/{PROJECT_ID}",
            json=payload,
            timeout=180  # Longer timeout for LLM response
        )
        
        print(f"\nStatus: {response.status_code}")
        result = response.json()
        
        if "answer" in result:
            print(f"\n{'─'*50}")
            print(f"{Colors.BOLD}ANSWER:{Colors.END}")
            print('─'*50)
            print(result['answer'])
            print('─'*50)
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_quick_test():
    """Run just the health check"""
    print_divider("Quick Health Check")
    if test_health():
        print_success("API is healthy and responding!")
        return True
    else:
        print_error("API is not responding")
        return False

def run_full_test():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'🚀'*30}")
    print(f"\n  RAG APPLICATION - REMOTE PIPELINE TEST")
    print(f"  Target: {BASE_URL}")
    print(f"\n{'🚀'*30}{Colors.END}")
    
    results = {}
    
    # Run tests
    results["health"] = test_health()
    if not results["health"]:
        print_error("Health check failed. Stopping tests.")
        return
    
    results["welcome"] = test_welcome()
    
    success, file_name = test_upload()
    results["upload"] = success
    
    if results["upload"]:
        results["process"] = test_process()
        
        print_info("Waiting 3 seconds for embeddings to process...")
        time.sleep(3)
        
        results["index"] = test_index()
        
        print_info("Waiting 3 seconds for indexing to complete...")
        time.sleep(3)
        
        results["index_info"] = test_index_info()
        results["search"] = test_search()
        results["answer"] = test_answer()
    
    # Summary
    print_divider("TEST RESULTS SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name.upper():15}")
        else:
            print_error(f"{test_name.upper():15}")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print(f"  {Colors.GREEN}🎉 ALL TESTS PASSED! Remote RAG Pipeline is functional!{Colors.END}")
    else:
        print(f"  {Colors.YELLOW}⚠️  Some tests failed. Check the output above.{Colors.END}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_full_test()
