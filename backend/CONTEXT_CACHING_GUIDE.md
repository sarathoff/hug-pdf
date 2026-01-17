# Context Caching Quick Start Guide

## What is Context Caching?

Context caching allows you to cache frequently used content (system prompts, instructions, reference documents) in Gemini's API, so you don't have to send them with every request. **Cached tokens cost ~90% less** than regular input tokens.

## Quick Implementation

### 1. Install/Update Google GenAI SDK

```bash
pip install --upgrade google-genai
```

### 2. Use the CacheService

```python
from services.cache_service import CacheService

# Initialize
cache_service = CacheService()

# Create or get cache
cache_name = cache_service.get_or_create_cache(
    cache_key="my_system_prompt_v1",
    system_instruction="Your long system prompt here...",
    ttl_seconds=3600  # 1 hour
)

# Use in generation
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents="User prompt",
    cached_content=cache_name
)
```

### 3. Monitor Savings

```python
stats = cache_service.get_stats()
print(f"Cost saved: ${stats['cost_saved_usd']}")
print(f"Tokens saved: {stats['tokens_saved']}")
print(f"Hit rate: {stats['hit_rate_percent']}%")
```

## Best Practices

### ✅ DO Cache:
- System prompts that don't change often
- Base instructions used across all requests
- Scraped web content in research mode
- Reference documents or examples
- Content > 1024 tokens (minimum for caching)

### ❌ DON'T Cache:
- User-specific prompts
- Frequently changing content
- Small prompts (< 1024 tokens)
- Real-time data

## Cache TTL Guidelines

| Content Type | Recommended TTL | Reason |
|--------------|----------------|---------|
| Base instructions | 1-2 hours | Rarely changes |
| System prompts | 1 hour | May need updates |
| Research content | 30 minutes | Content freshness |
| User context | 15 minutes | Session-specific |

## Cost Comparison

### Without Caching
```
Research mode request:
- System prompt: 1,000 tokens
- Scraped content: 10,000 tokens
- User prompt: 100 tokens
Total input: 11,100 tokens × $0.00015/1K = $0.001665
```

### With Caching
```
Research mode request (after first):
- Cached content: 11,000 tokens × $0.000015/1K = $0.000165
- User prompt: 100 tokens × $0.00015/1K = $0.000015
Total: $0.00018 (89% savings!)
```

## Integration Checklist

- [ ] Install/update google-genai SDK
- [ ] Create `CacheService` class
- [ ] Identify cacheable content in your prompts
- [ ] Add cache keys with version numbers
- [ ] Implement cache in `generate_latex_from_prompt()`
- [ ] Add cache statistics endpoint
- [ ] Monitor cache hit rates
- [ ] Adjust TTL based on usage patterns

## Troubleshooting

### Cache not working?
1. Check content is > 1024 tokens
2. Verify API key has caching enabled
3. Check cache hasn't expired
4. Review Gemini API documentation for latest syntax

### Low hit rate?
1. Increase TTL if content doesn't change often
2. Ensure cache keys are consistent
3. Check if you're creating too many unique caches

### High costs still?
1. Monitor which requests aren't using cache
2. Identify patterns in uncached requests
3. Consider caching more content
4. Review cache TTL settings

## API Endpoint Example

Add to `server.py`:

```python
@api_router.get("/cache/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    stats = gemini_service.get_cache_statistics()
    return stats
```

## Next Steps

1. **Start small**: Cache base instructions first
2. **Monitor**: Track hit rates and cost savings
3. **Optimize**: Adjust TTL and cache keys based on data
4. **Scale**: Add more caching as you see benefits

## Resources

- [Google Gemini Caching Documentation](https://ai.google.dev/gemini-api/docs/caching)
- [Pricing Information](https://ai.google.dev/pricing)
- Your implementation plan: `implementation_plan.md`
