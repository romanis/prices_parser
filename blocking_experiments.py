#!/usr/bin/env python3
"""
Experimental framework to understand website blocking conditions.
Systematically tests different configurations to identify blocking triggers.
"""

import time
import random
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

import requests
import cloudscraper
from fake_useragent import UserAgent

import config


class BlockDetector:
    """Detect if a response indicates blocking."""
    
    BLOCK_STATUS_CODES = [403, 429, 503]
    
    BLOCK_PATTERNS = [
        'access denied', 'blocked', 'captcha', 'cloudflare',
        'security check', 'rate limit', 'too many requests',
        'bot detection', 'suspicious activity'
    ]
    
    @classmethod
    def is_blocked(cls, response: requests.Response) -> Tuple[bool, str]:
        """
        Check if response indicates blocking.
        
        Returns:
            (is_blocked, reason)
        """
        # Check status code
        if response.status_code in cls.BLOCK_STATUS_CODES:
            return True, f"Status {response.status_code}"
        
        # Check content
        content = response.text.lower()
        for pattern in cls.BLOCK_PATTERNS:
            if pattern in content:
                return True, f"Pattern: {pattern}"
        
        # Check response size (blocked pages often short)
        if response.status_code == 200 and len(content) < 500:
            return True, f"Suspicious short response: {len(content)} bytes"
        
        return False, "OK"


class ExperimentLogger:
    """Log experiment results."""
    
    def __init__(self, output_dir: str = 'experiments'):
        import os
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.current_experiment = None
        self.results = []
    
    def start_experiment(self, experiment_id: str, config: Dict):
        """Start logging a new experiment."""
        self.current_experiment = {
            'experiment_id': experiment_id,
            'started_at': datetime.now().isoformat(),
            'configuration': config,
            'requests': [],
            'blocks': [],
            'stats': {}
        }
    
    def log_request(self, success: bool, status_code: int, response_time: float, 
                    blocked: bool, block_reason: str = ""):
        """Log individual request."""
        if self.current_experiment is None:
            return
        
        self.current_experiment['requests'].append({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'status_code': status_code,
            'response_time': response_time,
            'blocked': blocked,
            'block_reason': block_reason
        })
        
        if blocked:
            self.current_experiment['blocks'].append({
                'request_number': len(self.current_experiment['requests']),
                'status_code': status_code,
                'reason': block_reason,
                'timestamp': datetime.now().isoformat()
            })
    
    def end_experiment(self):
        """Finish and save experiment."""
        if self.current_experiment is None:
            return
        
        # Calculate statistics
        requests = self.current_experiment['requests']
        total = len(requests)
        successful = sum(1 for r in requests if r['success'])
        blocked = sum(1 for r in requests if r['blocked'])
        
        response_times = [r['response_time'] for r in requests if r['response_time'] > 0]
        
        self.current_experiment['stats'] = {
            'total_requests': total,
            'successful_requests': successful,
            'blocked_requests': blocked,
            'success_rate': successful / total if total > 0 else 0,
            'block_rate': blocked / total if total > 0 else 0,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'first_block_at': self.current_experiment['blocks'][0]['request_number'] 
                              if self.current_experiment['blocks'] else None
        }
        
        self.current_experiment['ended_at'] = datetime.now().isoformat()
        
        # Save to file
        filename = f"{self.output_dir}/{self.current_experiment['experiment_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.current_experiment, f, indent=2)
        
        print(f"\n✓ Experiment saved: {filename}")
        
        # Store for analysis
        self.results.append(self.current_experiment)
        self.current_experiment = None


class BlockingExperiments:
    """Run systematic experiments to understand blocking."""
    
    def __init__(self, target_url: str = 'https://5ka.ru', quick_mode: bool = False):
        self.target_url = target_url
        self.quick_mode = quick_mode
        self.logger = ExperimentLogger()
        self.ua = UserAgent()
        
        # Adjust iterations for quick mode
        self.iterations = 20 if quick_mode else 50
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.log = logging.getLogger(__name__)
    
    def _make_request(self, session: requests.Session, headers: Dict, 
                      proxies: Optional[Dict] = None) -> Tuple[bool, int, float, bool, str]:
        """
        Make a single request and return results.
        
        Returns:
            (success, status_code, response_time, blocked, block_reason)
        """
        try:
            start_time = time.time()
            response = session.get(
                self.target_url,
                headers=headers,
                proxies=proxies,
                timeout=30
            )
            response_time = time.time() - start_time
            
            # Check if blocked
            blocked, block_reason = BlockDetector.is_blocked(response)
            
            success = response.status_code == 200 and not blocked
            
            return success, response.status_code, response_time, blocked, block_reason
            
        except requests.exceptions.RequestException as e:
            self.log.error(f"Request failed: {str(e)}")
            return False, 0, 0, True, f"Exception: {str(e)}"
    
    def experiment_request_frequency(self):
        """Experiment 1: Test different request frequencies."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 1: Request Frequency Threshold")
        print("=" * 70)
        
        # Test different requests per minute
        rpm_values = [6, 12, 20, 30, 60] if not self.quick_mode else [6, 12, 20]
        
        for rpm in rpm_values:
            delay = 60.0 / rpm
            
            config = {
                'requests_per_minute': rpm,
                'delay_seconds': delay,
                'user_agent': 'Chrome',
                'headers': 'full'
            }
            
            print(f"\nTesting {rpm} requests/minute (delay: {delay:.2f}s)...")
            
            self.logger.start_experiment(f'freq_rpm_{rpm}', config)
            
            session = requests.Session()
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            headers['User-Agent'] = self.ua.chrome
            
            for i in range(self.iterations):
                success, status, resp_time, blocked, reason = self._make_request(session, headers)
                self.logger.log_request(success, status, resp_time, blocked, reason)
                
                if blocked:
                    print(f"  ⚠️  BLOCK at request {i+1}: {reason}")
                
                print(f"  Request {i+1}/{self.iterations}: {'✓' if success else '✗'} "
                      f"({status}, {resp_time:.2f}s)", end='\r')
                
                time.sleep(delay)
            
            self.logger.end_experiment()
    
    def experiment_delays(self):
        """Experiment 2: Test different delay patterns."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 2: Delay Sensitivity")
        print("=" * 70)
        
        delay_configs = [
            ('fixed_1s', 1.0, 1.0),
            ('fixed_2s', 2.0, 2.0),
            ('fixed_5s', 5.0, 5.0),
            ('random_1_3s', 1.0, 3.0),
            ('random_2_5s', 2.0, 5.0),
        ]
        
        if self.quick_mode:
            delay_configs = delay_configs[:3]
        
        for name, min_delay, max_delay in delay_configs:
            config = {
                'delay_type': name,
                'min_delay': min_delay,
                'max_delay': max_delay,
                'iterations': self.iterations
            }
            
            print(f"\nTesting {name}...")
            
            self.logger.start_experiment(f'delay_{name}', config)
            
            session = requests.Session()
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            headers['User-Agent'] = self.ua.chrome
            
            for i in range(self.iterations):
                success, status, resp_time, blocked, reason = self._make_request(session, headers)
                self.logger.log_request(success, status, resp_time, blocked, reason)
                
                if blocked:
                    print(f"  ⚠️  BLOCK at request {i+1}")
                
                print(f"  Request {i+1}/{self.iterations}: {'✓' if success else '✗'}", end='\r')
                
                # Apply delay
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)
            
            self.logger.end_experiment()
    
    def experiment_user_agents(self):
        """Experiment 3: Test different user agents."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 3: User Agent Impact")
        print("=" * 70)
        
        ua_configs = [
            ('chrome_modern', self.ua.chrome),
            ('firefox_modern', self.ua.firefox),
            ('safari', self.ua.safari),
            ('python_requests', 'python-requests/2.31.0'),
            ('empty', ''),
        ]
        
        for name, user_agent in ua_configs:
            config = {
                'user_agent_type': name,
                'user_agent': user_agent,
                'delay': 2.0
            }
            
            print(f"\nTesting {name}...")
            
            self.logger.start_experiment(f'ua_{name}', config)
            
            session = requests.Session()
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            headers['User-Agent'] = user_agent
            
            iterations = min(20, self.iterations)
            
            for i in range(iterations):
                success, status, resp_time, blocked, reason = self._make_request(session, headers)
                self.logger.log_request(success, status, resp_time, blocked, reason)
                
                if blocked:
                    print(f"  ⚠️  BLOCK at request {i+1}")
                
                print(f"  Request {i+1}/{iterations}: {'✓' if success else '✗'}", end='\r')
                
                time.sleep(2.0)
            
            self.logger.end_experiment()
    
    def experiment_session_persistence(self):
        """Experiment 4: Test session vs no session."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 4: Session Persistence")
        print("=" * 70)
        
        session_configs = [
            ('persistent_session', True),
            ('new_session_each', False),
        ]
        
        for name, use_persistent in session_configs:
            config = {
                'session_type': name,
                'persistent': use_persistent,
                'delay': 2.0
            }
            
            print(f"\nTesting {name}...")
            
            self.logger.start_experiment(f'session_{name}', config)
            
            persistent_session = requests.Session() if use_persistent else None
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            headers['User-Agent'] = self.ua.chrome
            
            for i in range(self.iterations):
                session = persistent_session if use_persistent else requests.Session()
                
                success, status, resp_time, blocked, reason = self._make_request(session, headers)
                self.logger.log_request(success, status, resp_time, blocked, reason)
                
                if blocked:
                    print(f"  ⚠️  BLOCK at request {i+1}")
                
                print(f"  Request {i+1}/{self.iterations}: {'✓' if success else '✗'}", end='\r')
                
                time.sleep(2.0)
            
            self.logger.end_experiment()
    
    def experiment_cloudscraper(self):
        """Experiment 5: Compare cloudscraper vs requests."""
        print("\n" + "=" * 70)
        print("EXPERIMENT 5: Cloudscraper Effectiveness")
        print("=" * 70)
        
        configs = [
            ('requests_library', False),
            ('cloudscraper', True),
        ]
        
        for name, use_cloudscraper in configs:
            config = {
                'library': name,
                'cloudscraper': use_cloudscraper,
                'delay': 2.0
            }
            
            print(f"\nTesting {name}...")
            
            self.logger.start_experiment(f'lib_{name}', config)
            
            if use_cloudscraper:
                session = cloudscraper.create_scraper()
            else:
                session = requests.Session()
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            headers['User-Agent'] = self.ua.chrome
            
            iterations = min(30, self.iterations)
            
            for i in range(iterations):
                success, status, resp_time, blocked, reason = self._make_request(session, headers)
                self.logger.log_request(success, status, resp_time, blocked, reason)
                
                if blocked:
                    print(f"  ⚠️  BLOCK at request {i+1}")
                
                print(f"  Request {i+1}/{iterations}: {'✓' if success else '✗'}", end='\r')
                
                time.sleep(2.0)
            
            self.logger.end_experiment()
    
    def analyze_results(self):
        """Analyze all experiment results."""
        print("\n" + "=" * 70)
        print("EXPERIMENT ANALYSIS")
        print("=" * 70)
        
        import os
        import glob
        
        # Load all experiment files
        experiment_files = glob.glob(f"{self.logger.output_dir}/*.json")
        
        if not experiment_files:
            print("No experiment results found.")
            return
        
        results_by_type = defaultdict(list)
        
        for filepath in experiment_files:
            with open(filepath, 'r') as f:
                data = json.load(f)
                exp_type = data['experiment_id'].split('_')[0]
                results_by_type[exp_type].append(data)
        
        # Analyze each experiment type
        for exp_type, experiments in results_by_type.items():
            print(f"\n{'='*70}")
            print(f"{exp_type.upper()} EXPERIMENTS")
            print(f"{'='*70}")
            
            for exp in experiments:
                stats = exp['stats']
                print(f"\nConfiguration: {exp['experiment_id']}")
                print(f"  Success Rate:    {stats['success_rate']*100:.1f}%")
                print(f"  Block Rate:      {stats['block_rate']*100:.1f}%")
                print(f"  Avg Response:    {stats['avg_response_time']:.2f}s")
                print(f"  First Block At:  {stats['first_block_at'] or 'N/A'}")
        
        # Find best configurations
        print(f"\n{'='*70}")
        print("RECOMMENDATIONS")
        print(f"{'='*70}")
        
        all_experiments = [exp for exps in results_by_type.values() for exp in exps]
        
        # Sort by success rate
        best_performers = sorted(all_experiments, 
                                key=lambda x: x['stats']['success_rate'], 
                                reverse=True)[:5]
        
        print("\nTop 5 Best Configurations:")
        for i, exp in enumerate(best_performers, 1):
            stats = exp['stats']
            print(f"\n{i}. {exp['experiment_id']}")
            print(f"   Success Rate: {stats['success_rate']*100:.1f}%")
            print(f"   Avg Response: {stats['avg_response_time']:.2f}s")
            print(f"   Configuration: {exp['configuration']}")


def main():
    """Run experiments based on command line arguments."""
    parser = argparse.ArgumentParser(description='Run blocking condition experiments')
    parser.add_argument('--experiment', choices=[
        'request_frequency', 'delays', 'user_agents', 
        'session', 'cloudscraper', 'all'
    ], help='Specific experiment to run')
    parser.add_argument('--run-all', action='store_true', help='Run all experiments')
    parser.add_argument('--analyze', action='store_true', help='Analyze existing results')
    parser.add_argument('--quick', action='store_true', help='Quick mode (fewer iterations)')
    parser.add_argument('--target', default='https://5ka.ru', help='Target URL')
    
    args = parser.parse_args()
    
    experiments = BlockingExperiments(target_url=args.target, quick_mode=args.quick)
    
    if args.analyze:
        experiments.analyze_results()
        return
    
    # Run experiments
    experiment_map = {
        'request_frequency': experiments.experiment_request_frequency,
        'delays': experiments.experiment_delays,
        'user_agents': experiments.experiment_user_agents,
        'session': experiments.experiment_session_persistence,
        'cloudscraper': experiments.experiment_cloudscraper,
    }
    
    if args.run_all or args.experiment == 'all':
        print("\n" + "="*70)
        print("RUNNING ALL EXPERIMENTS")
        print("="*70)
        print("\n⚠️  This will take significant time!")
        print("Consider running with --quick for faster results.\n")
        
        for exp_func in experiment_map.values():
            exp_func()
            time.sleep(30)  # Cooldown between experiments
    
    elif args.experiment:
        experiment_map[args.experiment]()
    
    else:
        print("Please specify an experiment or use --run-all")
        print("Example: python blocking_experiments.py --experiment delays")
        return
    
    # Auto-analyze after running experiments
    print("\n" + "="*70)
    print("Analyzing results...")
    experiments.analyze_results()


if __name__ == '__main__':
    main()

