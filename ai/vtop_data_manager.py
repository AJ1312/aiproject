#!/usr/bin/env python3
"""
VTOP Data Manager
Intelligent data fetching with caching and rate limiting to prevent session logout
"""

import subprocess
import tempfile
import json
from pathlib import Path
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
import sys


class VTOPDataManager:
    """Manages VTOP data fetching with intelligent caching and rate limiting"""
    
    def __init__(self, cache_duration_minutes=30):
        """
        Initialize data manager
        
        Args:
            cache_duration_minutes: How long to cache data before refreshing (default: 30 minutes)
        """
        self.cli_top_path = Path(__file__).parent.parent / 'cli-top'
        self.cache_file = Path(__file__).parent / 'current_semester_data.json'
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.last_fetch_time = None
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests
        self.last_request_time = None
        
        # Load last fetch time from cache metadata
        self._load_cache_metadata()
    
    def _load_cache_metadata(self):
        """Load cache metadata to check freshness"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if 'generated_at' in data:
                        self.last_fetch_time = datetime.fromisoformat(data['generated_at'])
            except:
                pass
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.cache_file.exists():
            return False
        
        if self.last_fetch_time is None:
            return False
        
        age = datetime.now() - self.last_fetch_time
        return age < self.cache_duration
    
    def _wait_for_rate_limit(self):
        """Enforce minimum interval between requests"""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                wait_time = self.min_request_interval - elapsed
                print(f"⏳ Rate limiting: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _fetch_from_vtop(self, force=False) -> Dict:
        """
        Fetch fresh data from VTOP
        
        Args:
            force: If True, bypass rate limiting (use carefully!)
            
        Returns:
            Dictionary with VTOP data
        """
        if not force:
            self._wait_for_rate_limit()
        
        print("🔄 Fetching fresh data from VTOP...")
        
        # Export to temp file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.close()
        
        try:
            # Export all data
            cmd = [str(self.cli_top_path), 'ai', 'export', '-o', temp_file.name]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=120,
                stdin=subprocess.DEVNULL  # Prevent TTY issues
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to export data: {result.stderr}")
            
            # Parse the exported data
            sys.path.insert(0, str(Path(__file__).parent))
            from parse_current_semester import parse_all_data_file
            
            data = parse_all_data_file(temp_file.name)
            
            # Add generation timestamp
            data['generated_at'] = datetime.now().isoformat()
            
            # Save to cache
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.last_fetch_time = datetime.now()
            
            print("✅ Data fetched and cached successfully!")
            return data
            
        finally:
            Path(temp_file.name).unlink(missing_ok=True)
    
    def get_data(self, use_cache=True) -> Dict:
        """
        Get VTOP data (from cache or fresh fetch)
        
        Args:
            use_cache: If True, use cached data if valid. If False, always fetch fresh.
            
        Returns:
            Dictionary with VTOP data
        """
        if use_cache and self._is_cache_valid():
            print("📦 Using cached data (still fresh)")
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        else:
            if use_cache:
                print("⚠️  Cache expired, fetching fresh data...")
            return self._fetch_from_vtop()
    
    def force_refresh(self) -> Dict:
        """Force a fresh fetch from VTOP, bypassing cache"""
        return self._fetch_from_vtop()
    
    def get_cache_age(self) -> Optional[timedelta]:
        """Get age of current cache"""
        if self.last_fetch_time is None:
            return None
        return datetime.now() - self.last_fetch_time
    
    def clear_cache(self):
        """Clear cached data"""
        if self.cache_file.exists():
            self.cache_file.unlink()
            self.last_fetch_time = None
            print("🗑️  Cache cleared")


# Global instance
_data_manager = None

def get_data_manager(cache_duration_minutes=30) -> VTOPDataManager:
    """Get global data manager instance"""
    global _data_manager
    if _data_manager is None:
        _data_manager = VTOPDataManager(cache_duration_minutes)
    return _data_manager


def get_vtop_data(use_cache=True) -> Dict:
    """
    Convenience function to get VTOP data
    
    Args:
        use_cache: Whether to use cached data if available
        
    Returns:
        Dictionary with VTOP data
    """
    manager = get_data_manager()
    return manager.get_data(use_cache=use_cache)


if __name__ == '__main__':
    # Test the data manager
    import argparse
    
    parser = argparse.ArgumentParser(description='VTOP Data Manager')
    parser.add_argument('--refresh', action='store_true', help='Force refresh data')
    parser.add_argument('--clear', action='store_true', help='Clear cache')
    parser.add_argument('--status', action='store_true', help='Show cache status')
    
    args = parser.parse_args()
    
    manager = get_data_manager()
    
    if args.clear:
        manager.clear_cache()
    elif args.status:
        age = manager.get_cache_age()
        if age:
            print(f"📊 Cache age: {age}")
            print(f"📊 Valid: {manager._is_cache_valid()}")
        else:
            print("📊 No cache")
    elif args.refresh:
        manager.force_refresh()
    else:
        data = manager.get_data()
        print(f"\n📊 Data loaded: {len(data.get('marks', []))} courses")
        print(f"📊 CGPA: {data.get('cgpa', 'N/A')}")
