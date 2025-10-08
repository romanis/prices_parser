# Blocking Experiments - Quick Start Guide

Run systematic experiments to understand what triggers website blocks and optimize your scraper settings.

## 🎯 Quick Start

### 1. Run a Single Experiment (Recommended for First Time)

```bash
# Test different delays (fastest, ~5 minutes)
python blocking_experiments.py --experiment delays --quick

# Test request frequencies (~10 minutes)
python blocking_experiments.py --experiment request_frequency --quick

# Test user agents (~5 minutes)
python blocking_experiments.py --experiment user_agents --quick
```

### 2. Analyze Results

```bash
# View summary report
python analyze_blocking.py

# Generate optimal configuration file
python analyze_blocking.py --generate-config
```

### 3. Apply Findings

```bash
# The generated config will be in optimal_config.py
# Update your config.py with the recommended settings
```

## 📋 Available Experiments

| Experiment | Duration | What It Tests | Command |
|------------|----------|---------------|---------|
| **delays** | 5-10 min | Optimal delay patterns | `--experiment delays` |
| **request_frequency** | 10-20 min | Max safe requests/minute | `--experiment request_frequency` |
| **user_agents** | 5-10 min | Which UAs get blocked | `--experiment user_agents` |
| **session** | 10-15 min | Session vs no session | `--experiment session` |
| **cloudscraper** | 5-10 min | Library effectiveness | `--experiment cloudscraper` |
| **all** | 1-2 hours | Complete test suite | `--run-all` |

## 🚀 Example Workflow

### Step 1: Quick Test (5 minutes)

```bash
# Test delay patterns (fastest)
python blocking_experiments.py --experiment delays --quick
```

**Output:**
```
======================================================================
EXPERIMENT 2: Delay Sensitivity
======================================================================

Testing fixed_1s...
  Request 20/20: ✓
✓ Experiment saved: experiments/delay_fixed_1s_20231006_120000.json

Testing fixed_2s...
  Request 20/20: ✓
✓ Experiment saved: experiments/delay_fixed_2s_20231006_120100.json

...

Analyzing results...
```

### Step 2: View Results (instant)

```bash
python analyze_blocking.py
```

**Output:**
```
================================================================================
                    BLOCKING EXPERIMENTS - SUMMARY REPORT
================================================================================

📊 Total Experiments: 5
📁 Experiment Types: 1
📅 Date Range: 2025-10-06

────────────────────────────────────────────────────────────────────────────────
📈 DELAY EXPERIMENTS
────────────────────────────────────────────────────────────────────────────────

Configuration                            Success    Blocks     Avg Time
────────────────────────────────────────────────────────────────────────────────
✓ Delay: random_2_5s                     100.0%     0.0%       1.23s
✓ Delay: fixed_5s                        95.0%      5.0%       1.15s
⚠ Delay: fixed_2s                        75.0%      25.0%      1.08s

📊 Statistics:
   Mean Success Rate:    90.0%
   Median Success Rate:  95.0%
   Mean Response Time:   1.15s

🏆 Best Configuration:
   ID: delay_random_2_5s
   Success Rate: 100.0%
   First Block: Request #None

================================================================================
💡 RECOMMENDATIONS
================================================================================

🥇 TOP 5 OVERALL CONFIGURATIONS:
────────────────────────────────────────────────────────────────────────────────

1. delay_random_2_5s
   Success Rate:  100.0%
   Block Rate:    0.0%
   Response Time: 1.23s
   First Block:   Request #None

📋 CONFIGURATION SUGGESTIONS:
────────────────────────────────────────────────────────────────────────────────

2. Delay Pattern:
   Best Pattern: random_2_5s
   Success Rate: 100.0%
   Use random delays between 2.0s and 5.0s
```

### Step 3: Apply Settings

```bash
# Generate optimal config
python analyze_blocking.py --generate-config

# Check the generated config
cat optimal_config.py
```

**Generated config:**
```python
"""
Optimal configuration based on blocking experiments.
Generated: 2025-10-06T12:05:00
"""

# Request delays (in seconds)
MIN_DELAY = 2.0
MAX_DELAY = 5.0

# Use random delays for more human-like behavior

# User agents - rotate between modern browsers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    ...
]

# Session handling
USE_SESSION = True

# Cloudscraper for Cloudflare bypass
USE_CLOUDSCRAPER = True
```

### Step 4: Update Your Scraper

```python
# In config.py - apply the recommendations
MIN_DELAY = 2.0  # From experiments
MAX_DELAY = 5.0  # From experiments
```

## 🎓 Understanding Results

### Success Rate
- **90-100%**: Excellent - safe for production
- **70-89%**: Good - acceptable with monitoring
- **50-69%**: Fair - needs improvement
- **< 50%**: Poor - avoid this configuration

### Block Rate
- **0-10%**: Safe zone
- **10-25%**: Caution zone
- **> 25%**: Danger zone

### Response Time
- **< 1s**: Fast
- **1-2s**: Normal
- **> 2s**: Slow (may indicate throttling)

## 📊 Reading Experiment Files

Results are saved in `experiments/` directory as JSON:

```json
{
  "experiment_id": "delay_random_2_5s",
  "started_at": "2025-10-06T12:00:00",
  "configuration": {
    "delay_type": "random_2_5s",
    "min_delay": 2.0,
    "max_delay": 5.0
  },
  "stats": {
    "total_requests": 20,
    "successful_requests": 20,
    "blocked_requests": 0,
    "success_rate": 1.0,
    "avg_response_time": 1.23
  },
  "blocks": []
}
```

## 🔧 Advanced Usage

### Custom Target URL

```bash
python blocking_experiments.py \
  --experiment delays \
  --target https://example.com
```

### Full Test Suite (Comprehensive)

```bash
# Warning: Takes 1-2 hours!
python blocking_experiments.py --run-all
```

### Analyze Specific Directory

```bash
python analyze_blocking.py --dir my_experiments/
```

## 💡 Pro Tips

### 1. Start Conservative
```bash
# Always start with quick mode first
python blocking_experiments.py --experiment delays --quick
```

### 2. Test During Off-Peak Hours
```bash
# Run at 2 AM - 5 AM local time for best results
```

### 3. Re-test Periodically
```bash
# Websites change their protection over time
# Re-run experiments monthly
```

### 4. Compare Before/After
```bash
# Run experiments before making changes
# Run again after to verify improvements
```

## ⚠️ Safety Guidelines

### DO:
- ✅ Run during off-peak hours
- ✅ Start with `--quick` mode
- ✅ Use reasonable delays (>= 1s)
- ✅ Stop if server shows signs of stress
- ✅ Respect robots.txt

### DON'T:
- ❌ Run during peak business hours
- ❌ Test with 0-second delays
- ❌ Overwhelm servers
- ❌ Run all experiments simultaneously
- ❌ Ignore block signals

## 🐛 Troubleshooting

### "No experiments found"
```bash
# Make sure you've run experiments first
python blocking_experiments.py --experiment delays --quick
```

### "All requests blocked"
```bash
# Website may have strong protection
# Try:
# 1. Longer delays
# 2. Different user agents
# 3. Cloudscraper
# 4. Selenium
```

### "Connection errors"
```bash
# Check internet connection
# Verify target URL is accessible
curl -I https://5ka.ru
```

## 📈 Interpreting Patterns

### Pattern 1: Gradual Degradation
```
Requests 1-10:   100% success
Requests 11-20:  80% success
Requests 21-30:  50% success
```
**Meaning**: Cumulative blocking - need longer delays or IP rotation

### Pattern 2: Immediate Blocking
```
Request 1: ✗ BLOCK
Request 2: ✗ BLOCK
```
**Meaning**: User agent or headers issue - change browser signature

### Pattern 3: Random Blocks
```
Request 5:  ✗ BLOCK
Request 15: ✗ BLOCK
Request 23: ✗ BLOCK
```
**Meaning**: Network issues or intermittent protection - add retries

### Pattern 4: Threshold Blocking
```
Requests 1-50:  100% success
Request 51:     ✗ BLOCK (all subsequent blocked)
```
**Meaning**: Hit rate limit - need IP rotation

## 📚 Next Steps

After running experiments:

1. **Update Configuration**
   ```bash
   # Apply findings to config.py
   vim config.py
   ```

2. **Test in Production**
   ```bash
   # Run your scraper with new settings
   python main_with_auto_proxy.py --max-pages 5
   ```

3. **Monitor Performance**
   ```bash
   # Check logs for block rates
   tail -f scraper.log | grep -i block
   ```

4. **Iterate**
   ```bash
   # Re-run experiments if needed
   # Fine-tune based on production data
   ```

## 🎯 Success Criteria

You've found optimal settings when:
- ✅ Success rate > 90%
- ✅ No blocks in first 50 requests
- ✅ Consistent performance over time
- ✅ Acceptable speed for your use case
- ✅ Sustainable resource usage

## 📞 Need Help?

Check:
1. `BLOCKING_EXPERIMENTS.md` - Full experimental framework
2. `scraper.log` - Detailed logs
3. `experiments/*.json` - Raw experiment data

---

**Remember**: The goal is to find settings that work reliably while respecting the target website!

