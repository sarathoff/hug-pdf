"""
Add these endpoints to server.py to monitor cache performance

These endpoints allow you to:
1. Get cache statistics (hit rate, cost savings, etc.)
2. Invalidate specific caches
3. Cleanup expired caches
"""

# Add to your imports in server.py:
# from services.cache_service import CacheService

# Initialize cache service (add after other service initializations around line 78):
# cache_service = CacheService()

# Add these routes to your api_router:

@api_router.get("/cache/stats")
async def get_cache_stats(current_user: Optional[dict] = Depends(get_current_user)):
    """
    Get cache performance statistics
    
    Returns:
        - cache_hits: Number of times cache was used
        - cache_misses: Number of times cache was not available
        - hit_rate_percent: Percentage of requests that used cache
        - tokens_saved: Total tokens saved by caching
        - cost_saved_usd: Estimated cost savings in USD
        - active_caches: Number of active caches
    """
    try:
        # Get stats from gemini_service's cache
        stats = gemini_service.cache_service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/cache/invalidate/{cache_key}")
async def invalidate_cache(
    cache_key: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Invalidate a specific cache (admin only)
    
    Useful when you update system prompts and want to force cache refresh
    """
    # Optional: Add admin check
    # if current_user.get('plan') != 'admin':
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        success = gemini_service.cache_service.invalidate_cache(cache_key)
        
        if success:
            return {
                "success": True,
                "message": f"Cache {cache_key} invalidated successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Cache {cache_key} not found"
            }
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/cache/cleanup")
async def cleanup_expired_caches(current_user: dict = Depends(get_current_user)):
    """
    Cleanup expired caches from metadata
    
    This is automatically done when getting caches, but you can manually trigger it
    """
    try:
        count = gemini_service.cache_service.cleanup_expired_caches()
        return {
            "success": True,
            "message": f"Cleaned up {count} expired caches"
        }
    except Exception as e:
        logger.error(f"Error cleaning up caches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Example: How to modify gemini_service initialization to include cache_service
# In server.py, modify the GeminiService initialization:

"""
# Before (line 73):
gemini_service = GeminiService()

# After:
gemini_service = GeminiService()
# Add cache service to gemini_service if not already initialized
if not hasattr(gemini_service, 'cache_service'):
    from services.cache_service import CacheService
    gemini_service.cache_service = CacheService()
"""

# Frontend integration example:

"""
// In your React frontend, add a cache stats component:

const CacheStats = () => {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/cache/stats`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        setStats(data.stats);
      } catch (error) {
        console.error('Failed to fetch cache stats:', error);
      }
    };
    
    fetchStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);
  
  if (!stats) return null;
  
  return (
    <div className="cache-stats">
      <h3>Cache Performance</h3>
      <p>Hit Rate: {stats.hit_rate_percent}%</p>
      <p>Tokens Saved: {stats.tokens_saved.toLocaleString()}</p>
      <p>Cost Saved: ${stats.cost_saved_usd.toFixed(4)}</p>
      <p>Active Caches: {stats.active_caches}</p>
    </div>
  );
};
"""
