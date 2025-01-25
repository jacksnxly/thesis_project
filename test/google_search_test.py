from googlesearch import search
import time

def test_basic_search():
    print("Testing basic search...")
    try:
        for result in search("Python programming", num_results=5):
            print(f"- {result}")
        print("Basic search successful\n")
    except Exception as e:
        print(f"Basic search failed: {e}\n")

def test_advanced_features():
    print("Testing advanced features...")
    
    # Test with more results
    print("\nTesting num_results (100 results):")
    try:
        results = list(search("machine learning", num_results=100))
        print(f"Got {len(results)} results")
    except Exception as e:
        print(f"num_results test failed: {e}")
    
    # Test unique results
    print("\nTesting unique results:")
    try:
        results = list(search("data science", num_results=50, unique=True))
        print(f"Got {len(results)} unique results")
    except Exception as e:
        print(f"unique results test failed: {e}")
    
    # Test language setting
    print("\nTesting language (French):")
    try:
        for result in search("AI", lang="fr", num_results=5):
            print(f"- {result}")
    except Exception as e:
        print(f"language test failed: {e}")
    
    # Test region setting
    print("\nTesting region (US):")
    try:
        for result in search("startups", region="us", num_results=5):
            print(f"- {result}")
    except Exception as e:
        print(f"region test failed: {e}")
    
    # Test safe search
    print("\nTesting safe search (disabled):")
    try:
        for result in search("news", safe=None, num_results=5):
            print(f"- {result}")
    except Exception as e:
        print(f"safe search test failed: {e}")
    
    # Test advanced search
    print("\nTesting advanced search:")
    try:
        for result in search("Python", advanced=True, num_results=3):
            print(f"Title: {result.title}")
            print(f"URL: {result.url}")
            print(f"Description: {result.description}\n")
    except Exception as e:
        print(f"advanced search test failed: {e}")
    
    # Test sleep interval
    print("\nTesting sleep interval (5 seconds):")
    try:
        start_time = time.time()
        list(search("web development", sleep_interval=5, num_results=20))
        elapsed = time.time() - start_time
        print(f"Search took {elapsed:.1f} seconds (should be >15s)")
    except Exception as e:
        print(f"sleep interval test failed: {e}")

if __name__ == "__main__":
    test_basic_search()
    test_advanced_features()
