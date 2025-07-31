#!/usr/bin/env python3
"""
Memory monitoring utilities for video generation
"""

import psutil
import gc
import os
import logging
from functools import wraps
from typing import Dict, Any

class MemoryMonitor:
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 ** 2),  # Resident Set Size
            'vms_mb': memory_info.vms / (1024 ** 2),  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / (1024 ** 2),
            'total_mb': psutil.virtual_memory().total / (1024 ** 2)
        }
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage is within limits"""
        memory_usage = self.get_memory_usage()
        return memory_usage['rss_mb'] < self.max_memory_mb
    
    def force_cleanup(self):
        """Force garbage collection and memory cleanup"""
        # Run garbage collection multiple times
        for _ in range(3):
            gc.collect()
        
        # Log memory usage after cleanup
        memory_usage = self.get_memory_usage()
        self.logger.info(f"Memory after cleanup: {memory_usage['rss_mb']:.1f}MB")
    
    def memory_limit_decorator(self, func):
        """Decorator to monitor memory usage of functions"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check memory before execution
            initial_memory = self.get_memory_usage()
            self.logger.info(f"Memory before {func.__name__}: {initial_memory['rss_mb']:.1f}MB")
            
            if not self.check_memory_limit():
                self.logger.warning(f"Memory limit exceeded before {func.__name__}")
                self.force_cleanup()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Check memory after execution
                final_memory = self.get_memory_usage()
                memory_increase = final_memory['rss_mb'] - initial_memory['rss_mb']
                
                self.logger.info(f"Memory after {func.__name__}: {final_memory['rss_mb']:.1f}MB "
                               f"(+{memory_increase:.1f}MB)")
                
                # Force cleanup if memory usage is high
                if final_memory['rss_mb'] > self.max_memory_mb * 0.8:
                    self.logger.warning("High memory usage detected, forcing cleanup")
                    self.force_cleanup()
        
        return wrapper

# Global memory monitor instance
memory_monitor = MemoryMonitor(max_memory_mb=1024)  # 1GB limit

def monitor_memory(func):
    """Decorator to monitor memory usage"""
    return memory_monitor.memory_limit_decorator(func)

def check_available_memory(min_required_mb: int = 500) -> bool:
    """Check if enough memory is available for video generation"""
    memory_usage = memory_monitor.get_memory_usage()
    available_mb = memory_usage['available_mb']
    
    if available_mb < min_required_mb:
        logging.warning(f"Low memory: {available_mb:.1f}MB available, {min_required_mb}MB required")
        return False
    
    return True

def optimize_for_low_memory() -> Dict[str, Any]:
    """Return optimized settings for low memory environments"""
    return {
        'max_resolution': (1280, 720),  # 720p instead of 1080p
        'fps': 24,
        'video_bitrate': '400k',  # Lower bitrate
        'audio_bitrate': '64k',   # Lower audio bitrate
        'threads': 1,             # Single thread to save memory
        'preset': 'ultrafast',    # Fastest encoding
        'temp_cleanup': True      # Clean temp files immediately
    }

def get_memory_safe_settings(available_memory_mb: float) -> Dict[str, Any]:
    """Get video settings based on available memory"""
    if available_memory_mb < 512:  # Less than 512MB
        return {
            'resolution': (854, 480),   # 480p
            'fps': 20,
            'video_bitrate': '300k',
            'audio_bitrate': '48k',
            'threads': 1,
            'preset': 'ultrafast'
        }
    elif available_memory_mb < 1024:  # Less than 1GB
        return {
            'resolution': (1280, 720),  # 720p
            'fps': 24,
            'video_bitrate': '500k',
            'audio_bitrate': '64k',
            'threads': 2,
            'preset': 'fast'
        }
    else:  # 1GB or more
        return {
            'resolution': (1920, 1080), # 1080p
            'fps': 24,
            'video_bitrate': '800k',
            'audio_bitrate': '128k',
            'threads': 2,
            'preset': 'medium'
        }

# Example usage
if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test memory monitoring
    print("🔍 Memory Monitoring Test")
    
    memory_usage = memory_monitor.get_memory_usage()
    print(f"Current memory usage: {memory_usage['rss_mb']:.1f}MB ({memory_usage['percent']:.1f}%)")
    print(f"Available memory: {memory_usage['available_mb']:.1f}MB")
    
    # Check if we have enough memory for video generation
    if check_available_memory(500):
        print("✅ Sufficient memory for video generation")
    else:
        print("⚠️ Low memory - consider optimizing settings")
    
    # Get recommended settings
    settings = get_memory_safe_settings(memory_usage['available_mb'])
    print(f"Recommended settings: {settings}")
    
    # Test memory cleanup
    print("\n🧹 Testing memory cleanup...")
    memory_monitor.force_cleanup()
    
    final_memory = memory_monitor.get_memory_usage()
    print(f"Memory after cleanup: {final_memory['rss_mb']:.1f}MB")