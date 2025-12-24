"""Simple remote API test - no emojis for better PowerShell compatibility"""
import requests
import json
import time

BASE_URL = "https://rag-app-production-e4be.up.railway.app/api/v1"
PROJECT_ID = "remotetestproject"

def main():
    print("=" * 50)
    print("REMOTE API FULL TEST")
    print("=" * 50)
    print()

    results = {}

    # 1. Health
    print("1. Health Check...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=30)
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        results["health"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["health"] = False

    # 2. Welcome  
    print("\n2. Welcome Endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=30)
        print(f"   Status: {r.status_code}")
        results["welcome"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["welcome"] = False

    # 3. Upload
    print("\n3. Upload File...")
    try:
        test_content = """Machine Learning is a subset of AI that enables learning from data.
        It includes supervised learning, unsupervised learning, and reinforcement learning.
        Deep learning uses neural networks with multiple layers."""
        files = {"file": ("test.txt", test_content.encode(), "text/plain")}
        r = requests.post(f"{BASE_URL}/data/upload/{PROJECT_ID}", files=files, timeout=60)
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        results["upload"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["upload"] = False

    # 4. Process
    print("\n4. Process File (Chunking)...")
    try:
        payload = {"chunk_size": 200, "overlap": 20, "do_reset": 1}
        r = requests.post(f"{BASE_URL}/data/process/{PROJECT_ID}", json=payload, timeout=120)
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        results["process"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["process"] = False

    # 5. Index
    print("\n5. Index to Vector DB (Qdrant)...")
    try:
        r = requests.post(f"{BASE_URL}/nlp/index/push/{PROJECT_ID}", json={"do_reset": 1}, timeout=120)
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        results["index"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["index"] = False

    print("\n   Waiting 3 seconds for indexing...")
    time.sleep(3)

    # 6. Search
    print("\n6. Semantic Search...")
    try:
        payload = {"text": "What is machine learning?", "limit": 3}
        r = requests.post(f"{BASE_URL}/nlp/index/search/{PROJECT_ID}", json=payload, timeout=60)
        print(f"   Status: {r.status_code}")
        data = r.json()
        if "results" in data:
            print(f"   Found {len(data['results'])} results")
            for i, res in enumerate(data["results"][:2], 1):
                text = res.get("text", "")[:100]
                score = res.get("score", "N/A")
                print(f"   Result {i}: (score: {score}) {text}...")
        results["search"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["search"] = False

    # 7. Answer
    print("\n7. RAG Answer (using OpenRouter LLM)...")
    print("   This may take 30-60 seconds...")
    try:
        payload = {"text": "What is Machine Learning?", "limit": 3}
        r = requests.post(f"{BASE_URL}/nlp/index/answer/{PROJECT_ID}", json=payload, timeout=180)
        print(f"   Status: {r.status_code}")
        data = r.json()
        if "answer" in data:
            print(f"\n   ANSWER:")
            print(f"   {'-' * 40}")
            # Print answer in chunks to avoid line length issues
            answer = data["answer"]
            for i in range(0, len(answer), 80):
                print(f"   {answer[i:i+80]}")
            print(f"   {'-' * 40}")
        results["answer"] = r.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        results["answer"] = False

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        symbol = "[OK]" if passed else "[X]"
        print(f"   {symbol} {test_name.upper()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED! Remote RAG Pipeline is functional!")
    else:
        print("Some tests failed. Check the output above.")
    print("=" * 50)

if __name__ == "__main__":
    main()
