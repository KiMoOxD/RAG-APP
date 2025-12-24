"""
RAG Application Complete Test Suite
Tests: Upload → Process → Index → Search → Answer
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
PROJECT_ID = "testproject2"  # Fresh project

def print_divider(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_health():
    """Test health endpoint"""
    print_divider("Step 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_upload():
    """Test file upload"""
    print_divider("Step 2: Upload File")
    with open("test_document.txt", "rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        response = requests.post(
            f"{BASE_URL}/data/upload/{PROJECT_ID}",
            files=files
        )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200, result.get("FileName")

def test_process():
    """Test file processing"""
    print_divider("Step 3: Process File (Chunking)")
    payload = {
        "chunk_size": 200,
        "overlap": 20,
        "do_reset": 1
    }
    response = requests.post(
        f"{BASE_URL}/data/process/{PROJECT_ID}",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200

def test_index():
    """Test indexing into vector DB"""
    print_divider("Step 4: Index into Vector DB (Qdrant Cloud)")
    payload = {"do_reset": 1}
    response = requests.post(
        f"{BASE_URL}/nlp/index/push/{PROJECT_ID}",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200

def test_search():
    """Test vector search"""
    print_divider("Step 5: Semantic Search")
    payload = {
        "text": "What is machine learning?",
        "limit": 3
    }
    response = requests.post(
        f"{BASE_URL}/nlp/index/search/{PROJECT_ID}",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if "results" in result:
        print(f"Found {len(result['results'])} results:")
        for i, r in enumerate(result['results'], 1):
            print(f"\n  Result {i} (score: {r['score']:.4f}):")
            print(f"  {r['text'][:150]}...")
    else:
        print(f"Response: {json.dumps(result, indent=2)}")
    
    return response.status_code == 200

def test_answer():
    """Test RAG question answering"""
    print_divider("Step 6: RAG Answer (OpenRouter + Llama)")
    payload = {
        "text": "What is the difference between AI and Machine Learning?",
        "limit": 3
    }
    
    print(f"Question: {payload['text']}")
    print("\nGenerating answer...")
    
    response = requests.post(
        f"{BASE_URL}/nlp/index/answer/{PROJECT_ID}",
        json=payload,
        timeout=120
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    
    if "answer" in result:
        print(f"\n{'─'*40}")
        print("ANSWER:")
        print('─'*40)
        print(result['answer'])
        print('─'*40)
    else:
        print(f"Response: {json.dumps(result, indent=2)}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("\n" + "🚀"*30)
    print("\n  RAG APPLICATION - COMPLETE PIPELINE TEST")
    print("\n" + "🚀"*30)
    
    results = {}
    
    # Run tests
    results["health"] = test_health()
    
    success, file_name = test_upload()
    results["upload"] = success
    
    results["process"] = test_process()
    
    print("\n⏳ Waiting 2 seconds for embeddings to process...")
    time.sleep(2)
    
    results["index"] = test_index()
    
    print("\n⏳ Waiting 2 seconds for indexing to complete...")
    time.sleep(2)
    
    results["search"] = test_search()
    results["answer"] = test_answer()
    
    # Summary
    print_divider("TEST RESULTS SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        if not passed:
            all_passed = False
        print(f"  {test_name.upper():12} : {status}")
    
    print("\n" + "="*60)
    if all_passed:
        print("  🎉 ALL TESTS PASSED! RAG Pipeline is fully functional!")
    else:
        print("  ⚠️  Some tests failed. Check the output above.")
    print("="*60 + "\n")
