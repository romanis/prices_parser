# Website Blocking Conditions - Experimental Framework

A systematic approach to understand what triggers blocks and optimize scraper settings.

## 🎯 Objectives

1. **Identify blocking thresholds** - How many requests trigger blocks?
2. **Understand timing requirements** - What delays are safe?
3. **Evaluate detection methods** - What signals websites use?
4. **Optimize configurations** - Find the sweet spot for speed vs. safety
5. **Test anti-detection measures** - Which techniques work best?

## 📊 Experimental Variables

### Independent Variables (What We Control)

1. **Request Frequency**
   - Requests per minute (RPM): 1, 5, 10, 20, 30, 60
   - Delay between requests: 0s, 1s, 2s, 5s, 10s, 30s

2. **User Agent**
   - Modern browsers (Chrome, Firefox, Safari)
   - Old browsers
   - Mobile browsers
   - Bots/crawlers (Python-requests, curl)
   - No user agent

3. **Request Headers**
   - Full realistic headers
   - Minimal headers
   - Missing Accept-Language
   - Missing Referer
   - Suspicious header combinations

4. **Session Behavior**
   - New session each request
   - Persistent session
   - Session with cookies
   - Session timeout intervals

5. **IP Rotation**
   - Same IP throughout
   - IP change every N requests
   - Random IP rotation
   - Geographic location of IPs

6. **Request Patterns**
   - Linear sequential (page 1, 2, 3...)
   - Random pages
   - Repeated page visits
   - Deep vs. shallow crawling

7. **Browser Fingerprint**
   - Accept headers variation
   - TLS fingerprint
   - HTTP/2 vs HTTP/1.1
   - JavaScript execution

### Dependent Variables (What We Measure)

1. **Block Indicators**
   - HTTP status codes (403, 429, 503)
   - Response content (CAPTCHA, access denied)
   - Response time anomalies
   - Empty/malformed responses

2. **Performance Metrics**
   - Time to first block
   - Total successful requests before block
   - Recovery time after block
   - Success rate percentage

3. **Resource Metrics**
   - Bandwidth usage
   - CPU/memory consumption
   - Proxy costs (if applicable)

## 🧪 Experiment Series

### **Experiment 1: Request Frequency Threshold**
**Objective**: Find the maximum safe request rate

**Method**:
1. Start with 1 request per minute
2. Gradually increase frequency
3. Monitor for blocks
4. Identify threshold where blocks begin

**Variations**:
- Test at different times of day
- Test on different days of week
- Test with/without session persistence

### **Experiment 2: Delay Sensitivity**
**Objective**: Determine optimal delay between requests

**Method**:
1. Fixed delays: 0s, 1s, 2s, 3s, 5s, 10s, 30s
2. Random delays: uniform(min, max)
3. Human-like delays: normal distribution
4. Make 50 requests per configuration
5. Measure blocks and performance

### **Experiment 3: User Agent Impact**
**Objective**: Test which user agents trigger blocks

**Method**:
1. Test categories:
   - Modern browsers
   - Old browsers
   - Mobile devices
   - Known bots
   - Empty/missing UA
2. Same request pattern for each
3. Compare block rates

### **Experiment 4: Header Completeness**
**Objective**: Identify critical headers

**Method**:
1. Baseline: Full realistic headers
2. Remove one header at a time
3. Test minimal header set
4. Identify which headers matter most

**Test Cases**:
- Remove Accept
- Remove Accept-Language
- Remove Accept-Encoding
- Remove Referer
- Remove DNT
- Remove Connection
- Minimal (only User-Agent)
- Empty headers

### **Experiment 5: Session Persistence**
**Objective**: Test session vs. no session impact

**Method**:
1. New session per request
2. Persistent session (reuse)
3. Session with cookie handling
4. Session reset intervals
5. Compare block rates and performance

### **Experiment 6: IP Rotation Strategy**
**Objective**: Optimize IP rotation frequency

**Method**:
1. No rotation (same IP)
2. Rotate every request
3. Rotate every 5, 10, 20, 50 requests
4. Rotate only on block detection
5. Measure overhead vs. block prevention

### **Experiment 7: Request Pattern Analysis**
**Objective**: Test if request patterns affect blocking

**Method**:
1. Sequential: pages 1, 2, 3...
2. Random: pages 5, 2, 8, 1...
3. Repeated: same page multiple times
4. Burst: many requests quickly, then pause
5. Steady: consistent pacing
6. Compare block rates

### **Experiment 8: Time-of-Day Effects**
**Objective**: Identify best scraping times

**Method**:
1. Test same configuration at:
   - Night (2-5 AM)
   - Morning (6-9 AM)
   - Midday (12-2 PM)
   - Evening (6-9 PM)
2. Weekend vs. weekday
3. Measure block rates and success

### **Experiment 9: Geographic IP Analysis**
**Objective**: Test if IP location matters

**Method**:
1. Local IPs (same country as website)
2. Nearby countries
3. Distant countries
4. Residential vs. datacenter IPs
5. Compare block rates

### **Experiment 10: Cloudflare Bypass Effectiveness**
**Objective**: Test cloudscraper success rate

**Method**:
1. Raw requests library
2. Cloudscraper
3. Selenium (real browser)
4. Compare success rates and speed

### **Experiment 11: Concurrent Requests**
**Objective**: Test parallel vs. sequential scraping

**Method**:
1. Sequential: 1 request at a time
2. Concurrent: 2, 5, 10 parallel requests
3. Measure blocks, performance, efficiency
4. Find optimal parallelism

### **Experiment 12: Retry Strategy**
**Objective**: Optimize retry behavior after blocks

**Method**:
1. No retry
2. Immediate retry
3. Exponential backoff
4. Fixed delay retry
5. Switch IP and retry
6. Measure success recovery rate

## 📈 Metrics to Track

For each experiment, log:

```python
{
    "experiment_id": "exp_001",
    "timestamp": "2025-10-06T00:00:00",
    "configuration": {
        "delay": 2.0,
        "user_agent": "Chrome/119.0",
        "headers": "full",
        "proxy": "enabled"
    },
    "results": {
        "total_requests": 100,
        "successful_requests": 95,
        "blocked_requests": 5,
        "success_rate": 0.95,
        "avg_response_time": 1.23,
        "first_block_at": 23,
        "total_duration": 200.5
    },
    "blocks": [
        {
            "request_number": 23,
            "status_code": 429,
            "response_time": 0.5,
            "content_snippet": "rate limit"
        }
    ]
}
```

## 🛠️ Implementation

Use the provided `blocking_experiments.py` script:

```bash
# Run all experiments
python blocking_experiments.py --run-all

# Run specific experiment
python blocking_experiments.py --experiment request_frequency

# Quick test (fewer iterations)
python blocking_experiments.py --experiment delays --quick

# Analyze results
python blocking_experiments.py --analyze

# Generate report
python blocking_experiments.py --report
```

## 📊 Data Analysis

After experiments, analyze:

1. **Correlation Analysis**
   - Which variables most affect blocking?
   - Interaction effects between variables

2. **Threshold Detection**
   - Request frequency limit
   - Minimum safe delay
   - Session duration limit

3. **Cost-Benefit Analysis**
   - Speed vs. block rate tradeoff
   - Proxy costs vs. direct connection
   - Resource utilization optimization

4. **Pattern Recognition**
   - Time-based patterns
   - Cumulative effect over time
   - Recovery patterns after blocks

## ⚠️ Important Considerations

### Ethical Guidelines
1. ✅ Run experiments during off-peak hours
2. ✅ Use rate limiting even in tests
3. ✅ Don't overwhelm target servers
4. ✅ Respect robots.txt
5. ✅ Stop if requested by site operators

### Safety Measures
1. Start conservative (slow, safe settings)
2. Gradually increase load
3. Monitor server response times
4. Be prepared to stop immediately
5. Keep logs for analysis and debugging

### Legal Compliance
1. Check website Terms of Service
2. Ensure experiments comply with local laws
3. Get permission if scraping for commercial use
4. Document your methodology

## 📋 Experiment Checklist

Before starting:
- [ ] Read target website's Terms of Service
- [ ] Check robots.txt
- [ ] Set up logging infrastructure
- [ ] Prepare multiple proxy IPs (if using)
- [ ] Define stopping criteria
- [ ] Schedule during off-peak hours
- [ ] Set up monitoring alerts

During experiments:
- [ ] Monitor CPU/memory usage
- [ ] Watch for server response degradation
- [ ] Log all results consistently
- [ ] Note any anomalies
- [ ] Be ready to stop if issues arise

After experiments:
- [ ] Analyze data thoroughly
- [ ] Document findings
- [ ] Update scraper configuration
- [ ] Share learnings (if appropriate)
- [ ] Archive experiment data

## 🎓 Expected Outcomes

After completing experiments, you should know:

1. **Optimal Settings**
   - Safe request frequency
   - Best delay configuration
   - Required headers
   - Session strategy

2. **Risk Factors**
   - What triggers immediate blocks
   - Warning signs before blocks
   - Recovery strategies
   - Cost of being blocked

3. **Best Practices**
   - Most effective anti-detection measures
   - Resource-efficient configurations
   - Sustainable scraping strategies
   - When to use proxies

## 📝 Example Findings Template

```markdown
## Experiment Results: Request Frequency

**Date**: 2025-10-06
**Target**: 5ka.ru
**Duration**: 2 hours

### Findings:
- Threshold: ~15 requests/minute triggers blocks
- Safe rate: 10 requests/minute (0 blocks in 100 requests)
- Optimal: 12 requests/minute (95% success rate)
- Block recovery: 5-10 minutes cooldown needed

### Recommendations:
- Set MIN_DELAY = 5 seconds
- Set MAX_DELAY = 7 seconds
- Use random delays for variation
- Monitor for 429 status codes

### Configuration Update:
```python
MIN_DELAY = 5
MAX_DELAY = 7
MAX_REQUESTS_PER_MINUTE = 10
```
```

## 🔄 Continuous Testing

1. **Regular Re-testing**
   - Websites change protection over time
   - Re-run key experiments monthly
   - Update configurations as needed

2. **A/B Testing**
   - Test configuration changes
   - Compare before/after performance
   - Gradual rollout of changes

3. **Monitoring**
   - Track success rates in production
   - Alert on anomalies
   - Auto-adjust if block rates increase

---

**Remember**: The goal is to find sustainable settings that respect the target website while achieving your data collection objectives. Always err on the side of caution!

