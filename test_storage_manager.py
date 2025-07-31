#!/usr/bin/env python3
"""
Test the storage manager functionality
"""

import os
import time
from storage_manager import StorageManager

def create_test_files():
    """Create some test files with different ages"""
    output_dir = 'static/outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create files with different timestamps
    test_files = [
        ('old_video_1.mp4', 48),  # 48 hours old
        ('old_video_2.mp4', 36),  # 36 hours old
        ('recent_video_1.mp4', 12),  # 12 hours old
        ('recent_video_2.mp4', 2),   # 2 hours old
        ('new_video.mp4', 0.5),      # 30 minutes old
    ]
    
    current_time = time.time()
    
    for filename, hours_old in test_files:
        filepath = os.path.join(output_dir, filename)
        
        # Create file with some content
        with open(filepath, 'w') as f:
            f.write(f"Test video content for {filename}\n" * 1000)  # Make it reasonably sized
        
        # Set the modification time to simulate age
        old_time = current_time - (hours_old * 3600)
        os.utime(filepath, (old_time, old_time))
        
        print(f"Created test file: {filename} ({hours_old}h old)")

def test_storage_manager():
    print("🧪 Testing Storage Manager...")
    
    # Create test files
    print("\n1. Creating test files...")
    create_test_files()
    
    # Initialize storage manager
    storage_manager = StorageManager(
        output_folder='static/outputs',
        max_age_hours=24,
        max_storage_gb=0.1  # Very small limit for testing
    )
    
    # Get initial stats
    print("\n2. Initial storage stats:")
    stats = storage_manager.get_storage_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test age-based cleanup
    print("\n3. Testing age-based cleanup (24h limit)...")
    age_result = storage_manager.cleanup_old_files()
    print(f"   Deleted {age_result['deleted_count']} old files")
    print(f"   Freed {age_result['deleted_size_mb']:.2f} MB")
    
    # Test size-based cleanup
    print("\n4. Testing size-based cleanup...")
    size_result = storage_manager.cleanup_by_size(target_size_gb=0.05)  # Very small target
    print(f"   Deleted {size_result['deleted_count']} files for space")
    print(f"   Freed {size_result['deleted_size_mb']:.2f} MB")
    print(f"   Final size: {size_result['current_size_gb']:.3f} GB")
    
    # Test smart cleanup
    print("\n5. Testing smart cleanup...")
    # Create more test files
    create_test_files()
    
    smart_result = storage_manager.smart_cleanup()
    print(f"   Total deleted: {smart_result['total_deleted']} files")
    print(f"   Total freed: {smart_result['total_freed_mb']:.2f} MB")
    print(f"   Final size: {smart_result['final_size_gb']:.3f} GB")
    
    # Final stats
    print("\n6. Final storage stats:")
    final_stats = storage_manager.get_storage_stats()
    for key, value in final_stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n✅ Storage manager test completed!")

if __name__ == '__main__':
    test_storage_manager()