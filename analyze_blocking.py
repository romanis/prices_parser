#!/usr/bin/env python3
"""
Advanced analysis and visualization of blocking experiments.
"""

import json
import glob
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
import statistics


class BlockingAnalyzer:
    """Analyze blocking experiment results."""
    
    def __init__(self, experiments_dir: str = 'experiments'):
        self.experiments_dir = experiments_dir
        self.experiments = []
        self.load_experiments()
    
    def load_experiments(self):
        """Load all experiment files."""
        pattern = f"{self.experiments_dir}/*.json"
        files = glob.glob(pattern)
        
        for filepath in files:
            with open(filepath, 'r') as f:
                self.experiments.append(json.load(f))
        
        print(f"Loaded {len(self.experiments)} experiments")
    
    def summary_report(self):
        """Generate comprehensive summary report."""
        print("\n" + "=" * 80)
        print(" " * 20 + "BLOCKING EXPERIMENTS - SUMMARY REPORT")
        print("=" * 80)
        
        if not self.experiments:
            print("\nNo experiments found. Run experiments first!")
            return
        
        # Group by experiment type
        by_type = defaultdict(list)
        for exp in self.experiments:
            exp_type = exp['experiment_id'].split('_')[0]
            by_type[exp_type].append(exp)
        
        print(f"\n📊 Total Experiments: {len(self.experiments)}")
        print(f"📁 Experiment Types: {len(by_type)}")
        print(f"📅 Date Range: {self._get_date_range()}")
        
        # Analyze each type
        for exp_type, experiments in sorted(by_type.items()):
            self._analyze_experiment_type(exp_type, experiments)
        
        # Overall recommendations
        self._generate_recommendations()
    
    def _get_date_range(self):
        """Get date range of experiments."""
        if not self.experiments:
            return "N/A"
        
        dates = [exp.get('started_at', '') for exp in self.experiments if 'started_at' in exp]
        if not dates:
            return "N/A"
        
        dates.sort()
        start = dates[0].split('T')[0]
        end = dates[-1].split('T')[0]
        
        return f"{start} to {end}" if start != end else start
    
    def _analyze_experiment_type(self, exp_type: str, experiments: List[Dict]):
        """Analyze specific experiment type."""
        print(f"\n{'─' * 80}")
        print(f"📈 {exp_type.upper()} EXPERIMENTS")
        print(f"{'─' * 80}")
        
        # Sort by success rate
        experiments.sort(key=lambda x: x['stats']['success_rate'], reverse=True)
        
        print(f"\n{'Configuration':<40} {'Success':<10} {'Blocks':<10} {'Avg Time'}")
        print(f"{'-' * 80}")
        
        for exp in experiments:
            stats = exp['stats']
            config_summary = self._summarize_config(exp['experiment_id'], exp['configuration'])
            
            success_rate = f"{stats['success_rate']*100:.1f}%"
            block_rate = f"{stats['block_rate']*100:.1f}%"
            avg_time = f"{stats['avg_response_time']:.2f}s"
            
            # Color code success rate
            symbol = "✓" if stats['success_rate'] >= 0.9 else "⚠" if stats['success_rate'] >= 0.7 else "✗"
            
            print(f"{symbol} {config_summary:<38} {success_rate:<10} {block_rate:<10} {avg_time}")
        
        # Statistical summary
        success_rates = [exp['stats']['success_rate'] for exp in experiments]
        response_times = [exp['stats']['avg_response_time'] for exp in experiments if exp['stats']['avg_response_time'] > 0]
        
        if success_rates:
            print(f"\n📊 Statistics:")
            print(f"   Mean Success Rate:    {statistics.mean(success_rates)*100:.1f}%")
            print(f"   Median Success Rate:  {statistics.median(success_rates)*100:.1f}%")
            if len(success_rates) > 1:
                print(f"   StdDev Success Rate:  {statistics.stdev(success_rates)*100:.1f}%")
        
        if response_times:
            print(f"   Mean Response Time:   {statistics.mean(response_times):.2f}s")
            print(f"   Median Response Time: {statistics.median(response_times):.2f}s")
        
        # Find best configuration
        best = experiments[0]
        print(f"\n🏆 Best Configuration:")
        print(f"   ID: {best['experiment_id']}")
        print(f"   Success Rate: {best['stats']['success_rate']*100:.1f}%")
        print(f"   First Block: Request #{best['stats']['first_block_at'] or 'None'}")
        self._print_config(best['configuration'])
    
    def _summarize_config(self, exp_id: str, config: Dict) -> str:
        """Summarize configuration in one line."""
        # Extract key info based on experiment type
        if 'freq_' in exp_id:
            return f"RPM: {config.get('requests_per_minute', 'N/A')}"
        elif 'delay_' in exp_id:
            return f"Delay: {config.get('delay_type', 'N/A')}"
        elif 'ua_' in exp_id:
            return f"UA: {config.get('user_agent_type', 'N/A')}"
        elif 'session_' in exp_id:
            return f"Session: {config.get('session_type', 'N/A')}"
        elif 'lib_' in exp_id:
            return f"Library: {config.get('library', 'N/A')}"
        else:
            return exp_id[:38]
    
    def _print_config(self, config: Dict, indent: str = "   "):
        """Pretty print configuration."""
        for key, value in config.items():
            if isinstance(value, dict):
                print(f"{indent}{key}:")
                self._print_config(value, indent + "  ")
            else:
                print(f"{indent}{key}: {value}")
    
    def _generate_recommendations(self):
        """Generate configuration recommendations."""
        print(f"\n{'=' * 80}")
        print("💡 RECOMMENDATIONS")
        print(f"{'=' * 80}")
        
        # Find overall best performers
        all_sorted = sorted(self.experiments, 
                           key=lambda x: x['stats']['success_rate'], 
                           reverse=True)
        
        print(f"\n🥇 TOP 5 OVERALL CONFIGURATIONS:")
        print(f"{'-' * 80}")
        
        for i, exp in enumerate(all_sorted[:5], 1):
            stats = exp['stats']
            print(f"\n{i}. {exp['experiment_id']}")
            print(f"   Success Rate:  {stats['success_rate']*100:.1f}%")
            print(f"   Block Rate:    {stats['block_rate']*100:.1f}%")
            print(f"   Response Time: {stats['avg_response_time']:.2f}s")
            print(f"   First Block:   Request #{stats['first_block_at'] or 'None'}")
        
        # Specific recommendations
        print(f"\n📋 CONFIGURATION SUGGESTIONS:")
        print(f"{'-' * 80}")
        
        self._recommend_frequency()
        self._recommend_delays()
        self._recommend_user_agent()
        self._recommend_session()
        self._recommend_tools()
    
    def _recommend_frequency(self):
        """Recommend request frequency."""
        freq_exps = [e for e in self.experiments if 'freq_' in e['experiment_id']]
        if not freq_exps:
            return
        
        # Find highest RPM with >90% success
        safe_configs = [e for e in freq_exps if e['stats']['success_rate'] >= 0.9]
        
        if safe_configs:
            best = max(safe_configs, key=lambda x: x['configuration'].get('requests_per_minute', 0))
            rpm = best['configuration']['requests_per_minute']
            delay = best['configuration']['delay_seconds']
            
            print(f"\n1. Request Frequency:")
            print(f"   Recommended RPM: {rpm} requests/minute")
            print(f"   Delay: {delay:.1f} seconds between requests")
            print(f"   Expected Success Rate: {best['stats']['success_rate']*100:.1f}%")
        else:
            print(f"\n1. Request Frequency:")
            print(f"   ⚠️  All frequencies tested showed high block rates")
            print(f"   Recommendation: Start with 6 RPM (10s delay) and monitor")
    
    def _recommend_delays(self):
        """Recommend delay pattern."""
        delay_exps = [e for e in self.experiments if 'delay_' in e['experiment_id']]
        if not delay_exps:
            return
        
        best = max(delay_exps, key=lambda x: x['stats']['success_rate'])
        delay_type = best['configuration']['delay_type']
        
        print(f"\n2. Delay Pattern:")
        print(f"   Best Pattern: {delay_type}")
        print(f"   Success Rate: {best['stats']['success_rate']*100:.1f}%")
        
        if 'random' in delay_type:
            min_d = best['configuration']['min_delay']
            max_d = best['configuration']['max_delay']
            print(f"   Use random delays between {min_d}s and {max_d}s")
        else:
            print(f"   Use fixed delay of {best['configuration'].get('min_delay')}s")
    
    def _recommend_user_agent(self):
        """Recommend user agent."""
        ua_exps = [e for e in self.experiments if 'ua_' in e['experiment_id']]
        if not ua_exps:
            return
        
        best = max(ua_exps, key=lambda x: x['stats']['success_rate'])
        ua_type = best['configuration']['user_agent_type']
        
        print(f"\n3. User Agent:")
        print(f"   Best: {ua_type}")
        print(f"   Success Rate: {best['stats']['success_rate']*100:.1f}%")
        print(f"   Rotate between modern browser user agents")
    
    def _recommend_session(self):
        """Recommend session handling."""
        session_exps = [e for e in self.experiments if 'session_' in e['experiment_id']]
        if not session_exps:
            return
        
        best = max(session_exps, key=lambda x: x['stats']['success_rate'])
        session_type = best['configuration']['session_type']
        
        print(f"\n4. Session Handling:")
        print(f"   Best: {session_type}")
        print(f"   Success Rate: {best['stats']['success_rate']*100:.1f}%")
    
    def _recommend_tools(self):
        """Recommend tools and libraries."""
        lib_exps = [e for e in self.experiments if 'lib_' in e['experiment_id']]
        if not lib_exps:
            return
        
        best = max(lib_exps, key=lambda x: x['stats']['success_rate'])
        library = best['configuration']['library']
        
        print(f"\n5. Library/Tool:")
        print(f"   Best: {library}")
        print(f"   Success Rate: {best['stats']['success_rate']*100:.1f}%")
    
    def generate_config_file(self, output_file: str = 'optimal_config.py'):
        """Generate optimal configuration file based on experiments."""
        print(f"\n{'=' * 80}")
        print(f"GENERATING OPTIMAL CONFIGURATION: {output_file}")
        print(f"{'=' * 80}")
        
        # Find best from each category
        freq_exps = [e for e in self.experiments if 'freq_' in e['experiment_id']]
        delay_exps = [e for e in self.experiments if 'delay_' in e['experiment_id']]
        
        config_lines = [
            '"""',
            'Optimal configuration based on blocking experiments.',
            f'Generated: {datetime.now().isoformat()}',
            '"""',
            '',
        ]
        
        if freq_exps:
            safe = [e for e in freq_exps if e['stats']['success_rate'] >= 0.9]
            if safe:
                best = max(safe, key=lambda x: x['configuration'].get('requests_per_minute', 0))
                delay = best['configuration']['delay_seconds']
                config_lines.extend([
                    '# Request delays (in seconds)',
                    f'MIN_DELAY = {delay:.1f}',
                    f'MAX_DELAY = {delay * 1.5:.1f}',
                    '',
                ])
        
        if delay_exps:
            best = max(delay_exps, key=lambda x: x['stats']['success_rate'])
            if 'random' in best['configuration']['delay_type']:
                config_lines.append('# Use random delays for more human-like behavior')
        
        config_lines.extend([
            '# Retry settings',
            'MAX_RETRIES = 3',
            'RETRY_DELAY = 5',
            '',
            '# User agents - rotate between modern browsers',
            'USER_AGENTS = [',
            "    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',",
            "    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',",
            "    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',",
            ']',
            '',
            '# Session handling',
            'USE_SESSION = True',
            '',
            '# Cloudscraper for Cloudflare bypass',
            'USE_CLOUDSCRAPER = True',
            '',
        ])
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(config_lines))
        
        print(f"✓ Configuration saved to {output_file}")


def main():
    """Main analysis function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze blocking experiments')
    parser.add_argument('--dir', default='experiments', help='Experiments directory')
    parser.add_argument('--generate-config', action='store_true', help='Generate optimal config file')
    parser.add_argument('--report', default='summary', choices=['summary', 'detailed'], 
                       help='Report type')
    
    args = parser.parse_args()
    
    analyzer = BlockingAnalyzer(experiments_dir=args.dir)
    
    if not analyzer.experiments:
        print("\n⚠️  No experiments found!")
        print(f"Run experiments first: python blocking_experiments.py --experiment delays")
        return
    
    analyzer.summary_report()
    
    if args.generate_config:
        analyzer.generate_config_file()
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

