"""
Performance Diagnostic Script
Identifies which component is causing slowdown
"""

import asyncio
import time
import requests
from datetime import datetime

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_api(name, url, method="GET", json_data=None, timeout=10):
    """Test API endpoint with timing"""
    print(f"Testing {name}...", end=" ", flush=True)
    start = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=json_data, timeout=timeout)
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ OK ({elapsed:.2f}s)")
            return True, elapsed, response.json()
        else:
            print(f"❌ Failed (Status {response.status_code})")
            return False, elapsed, None
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"❌ TIMEOUT (>{timeout}s)")
        return False, elapsed, None
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error: {e}")
        return False, elapsed, None


async def test_social_media_collector():
    """Test social media collector directly"""
    print_header("Testing Social Media Collector")
    
    try:
        # Try to import the social aggregator
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        from services.enhanced_social_collector import EnhancedSocialMediaAggregator
        from dotenv import load_dotenv
        import urllib.parse
        
        load_dotenv()
        
        twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        if twitter_token:
            twitter_token = urllib.parse.unquote(twitter_token)
        
        redis_url = os.getenv('REDIS_URL')
        social_aggregator = EnhancedSocialMediaAggregator(
            twitter_token=twitter_token,
            reddit_id=os.getenv('REDDIT_CLIENT_ID'),
            reddit_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            redis_url=redis_url
        )
        
        keywords = ["AI"]
        print(f"Collecting trends for: {keywords}")
        
        start = time.time()
        
        # Test with timeout
        try:
            results = await asyncio.wait_for(
                social_aggregator.collect_all_trends(keywords, "US"),
                timeout=20.0
            )
            elapsed = time.time() - start
            
            print(f"\n✅ Collection completed in {elapsed:.2f}s")
            print(f"   Trends found: {len(results.get('merged_trends', []))}")
            
            # Show source breakdown
            by_source = results.get('by_source', {})
            print(f"   Twitter: {len(by_source.get('twitter', []))}")
            print(f"   Reddit: {len(by_source.get('reddit', []))}")
            print(f"   Google: {len(by_source.get('google_trends', []))}")
            
            return True
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start
            print(f"\n❌ TIMEOUT after {elapsed:.2f}s")
            print("   This is the main bottleneck!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              TrendForge Performance Diagnostic                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    BASE_URL = "http://localhost:8000"
    
    # Test 1: Basic connectivity
    print_header("TEST 1: Basic Connectivity")
    success, time1, data = test_api("Root endpoint", f"{BASE_URL}/", timeout=5)
    
    if not success:
        print("\n❌ Backend not responding. Please start the backend server.")
        return
    
    # Test 2: Health check
    print_header("TEST 2: Health Check")
    success, time2, health = test_api("Health endpoint", f"{BASE_URL}/health", timeout=5)
    
    if health:
        print("\nService Status:")
        services = health.get('services', {})
        for service, status in services.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {service}: {status}")
    
    # Test 3: Channel analysis (small dataset)
    print_header("TEST 3: Channel Analysis Speed")
    
    test_data = {
        "videos": [
            {
                "videoId": "test123",
                "title": "Test Video",
                "viewCount": 1000,
                "likeCount": 50,
                "commentCount": 10,
                "publishedAt": "2024-01-01T00:00:00Z",
                "description": "Test description"
            }
        ],
        "channel_data": {
            "subscriberCount": 10000,
            "title": "Test Channel",
            "description": "Test description"
        }
    }
    
    success, time3, result = test_api(
        "Channel analysis",
        f"{BASE_URL}/api/v2/analyze-channel",
        method="POST",
        json_data=test_data,
        timeout=30
    )
    
    if time3 > 10:
        print(f"   ⚠️ WARNING: Slow response ({time3:.2f}s)")
    
    # Test 4: Social media collection
    print_header("TEST 4: Social Media Collection")
    print("This is the most likely bottleneck...")
    
    asyncio.run(test_social_media_collector())
    
    # Test 5: Full analysis
    print_header("TEST 5: Full Analysis")
    
    full_request = {
        "videos": test_data["videos"],
        "channel_data": test_data["channel_data"],
        "geo": "US",
        "max_recommendations": 5,
        "enable_backtest": False,
        "use_simple_mode": False
    }
    
    success, time5, result = test_api(
        "Full analysis",
        f"{BASE_URL}/api/v2/full-analysis",
        method="POST",
        json_data=full_request,
        timeout=60
    )
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    print("Performance Breakdown:")
    print(f"  Root endpoint:      {time1:.2f}s")
    print(f"  Health check:       {time2:.2f}s")
    print(f"  Channel analysis:   {time3:.2f}s")
    print(f"  Full analysis:      {time5:.2f}s")
    
    # Identify bottleneck
    print("\n🔍 Bottleneck Analysis:")
    
    if time5 > 30:
        print("  ❌ Full analysis is TOO SLOW (>30s)")
        print("\n  Likely causes:")
        print("  1. Social media API calls timing out")
        print("  2. Reddit API not configured (hangs while retrying)")
        print("  3. No caching enabled")
        
        print("\n  💡 Quick Fixes:")
        print("  1. Use the quick fix version: app_v2.py (already applied)")
        print("  2. Enable simple_mode in requests")
        print("  3. Configure Redis for caching")
        print("  4. Configure Reddit API or disable it")
    elif time5 > 15:
        print("  ⚠️ Full analysis is SLOW (15-30s)")
        print("\n  💡 Suggestions:")
        print("  1. Enable caching (Redis)")
        print("  2. Reduce max_recommendations to 5")
        print("  3. Use simple_mode for faster results")
    else:
        print("  ✅ Performance is acceptable (<15s)")
    
    # Recommendations
    print("\n📝 Recommendations:")
    
    if not health.get('services', {}).get('cache'):
        print("  1. ⚡ Install and start Redis for 10x speedup")
        print("     brew services start redis  # macOS")
        print("     sudo systemctl start redis  # Ubuntu")
    
    if not health.get('services', {}).get('reddit'):
        print("  2. 🔧 Configure Reddit API or disable it in code")
        print("     Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
    
    print("  3. 🚀 Use simple_mode for immediate improvement")
    print("     Set use_simple_mode: true in full-analysis requests")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
