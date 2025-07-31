#!/usr/bin/env python3
"""
Storage Manager for automatic cleanup of generated videos
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import threading
import schedule

class StorageManager:
    def __init__(self, output_folder: str, max_age_hours: int = 24, max_storage_gb: float = 5.0):
        self.output_folder = output_folder
        self.max_age_hours = max_age_hours
        self.max_storage_gb = max_storage_gb
        self.logger = logging.getLogger(__name__)
        
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
    def get_folder_size_gb(self) -> float:
        """Calculate total size of output folder in GB"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(self.output_folder):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except Exception as e:
            self.logger.error(f"Error calculating folder size: {e}")
        
        return total_size / (1024 ** 3)  # Convert to GB
    
    def get_file_info(self) -> List[Dict]:
        """Get information about all files in output folder"""
        files_info = []
        
        try:
            for filename in os.listdir(self.output_folder):
                filepath = os.path.join(self.output_folder, filename)
                
                if os.path.isfile(filepath):
                    try:
                        stat = os.stat(filepath)
                        files_info.append({
                            'path': filepath,
                            'name': filename,
                            'size_mb': stat.st_size / (1024 ** 2),
                            'created_time': stat.st_ctime,
                            'modified_time': stat.st_mtime,
                            'age_hours': (time.time() - stat.st_mtime) / 3600
                        })
                    except (OSError, FileNotFoundError):
                        continue
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
        
        return files_info
    
    def cleanup_old_files(self) -> Dict:
        """Remove files older than max_age_hours"""
        files_info = self.get_file_info()
        old_files = [f for f in files_info if f['age_hours'] > self.max_age_hours]
        
        deleted_count = 0
        deleted_size_mb = 0
        errors = []
        
        for file_info in old_files:
            try:
                os.remove(file_info['path'])
                deleted_count += 1
                deleted_size_mb += file_info['size_mb']
                self.logger.info(f"Deleted old file: {file_info['name']} ({file_info['age_hours']:.1f}h old)")
            except Exception as e:
                error_msg = f"Failed to delete {file_info['name']}: {e}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        return {
            'deleted_count': deleted_count,
            'deleted_size_mb': deleted_size_mb,
            'errors': errors,
            'remaining_files': len(files_info) - deleted_count
        }
    
    def cleanup_by_size(self, target_size_gb: float = None) -> Dict:
        """Remove oldest files until folder size is under target"""
        if target_size_gb is None:
            target_size_gb = self.max_storage_gb
        
        current_size = self.get_folder_size_gb()
        if current_size <= target_size_gb:
            return {
                'deleted_count': 0,
                'deleted_size_mb': 0,
                'current_size_gb': current_size,
                'target_size_gb': target_size_gb,
                'cleanup_needed': False
            }
        
        files_info = self.get_file_info()
        # Sort by modification time (oldest first)
        files_info.sort(key=lambda x: x['modified_time'])
        
        deleted_count = 0
        deleted_size_mb = 0
        errors = []
        
        for file_info in files_info:
            if self.get_folder_size_gb() <= target_size_gb:
                break
                
            try:
                os.remove(file_info['path'])
                deleted_count += 1
                deleted_size_mb += file_info['size_mb']
                self.logger.info(f"Deleted for space: {file_info['name']} ({file_info['size_mb']:.1f}MB)")
            except Exception as e:
                error_msg = f"Failed to delete {file_info['name']}: {e}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        return {
            'deleted_count': deleted_count,
            'deleted_size_mb': deleted_size_mb,
            'current_size_gb': self.get_folder_size_gb(),
            'target_size_gb': target_size_gb,
            'cleanup_needed': True,
            'errors': errors
        }
    
    def smart_cleanup(self) -> Dict:
        """Perform intelligent cleanup based on age and size"""
        self.logger.info("Starting smart cleanup...")
        
        # First, remove old files
        age_cleanup = self.cleanup_old_files()
        
        # Then, check if we need size-based cleanup
        size_cleanup = self.cleanup_by_size()
        
        total_result = {
            'age_cleanup': age_cleanup,
            'size_cleanup': size_cleanup,
            'total_deleted': age_cleanup['deleted_count'] + size_cleanup['deleted_count'],
            'total_freed_mb': age_cleanup['deleted_size_mb'] + size_cleanup['deleted_size_mb'],
            'final_size_gb': self.get_folder_size_gb(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Smart cleanup completed: {total_result['total_deleted']} files deleted, "
                        f"{total_result['total_freed_mb']:.1f}MB freed")
        
        return total_result
    
    def get_storage_stats(self) -> Dict:
        """Get current storage statistics"""
        files_info = self.get_file_info()
        
        if not files_info:
            return {
                'total_files': 0,
                'total_size_gb': 0,
                'oldest_file_hours': 0,
                'newest_file_hours': 0,
                'average_file_size_mb': 0
            }
        
        total_size_gb = sum(f['size_mb'] for f in files_info) / 1024
        oldest_age = max(f['age_hours'] for f in files_info)
        newest_age = min(f['age_hours'] for f in files_info)
        avg_size_mb = sum(f['size_mb'] for f in files_info) / len(files_info)
        
        return {
            'total_files': len(files_info),
            'total_size_gb': total_size_gb,
            'oldest_file_hours': oldest_age,
            'newest_file_hours': newest_age,
            'average_file_size_mb': avg_size_mb,
            'files_over_24h': len([f for f in files_info if f['age_hours'] > 24]),
            'storage_usage_percent': (total_size_gb / self.max_storage_gb) * 100 if self.max_storage_gb > 0 else 0
        }
    
    def start_scheduled_cleanup(self, interval_hours: int = 6):
        """Start automatic cleanup on schedule"""
        def run_cleanup():
            try:
                result = self.smart_cleanup()
                self.logger.info(f"Scheduled cleanup completed: {result}")
            except Exception as e:
                self.logger.error(f"Scheduled cleanup failed: {e}")
        
        # Schedule cleanup every N hours
        schedule.every(interval_hours).hours.do(run_cleanup)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        self.logger.info(f"Scheduled cleanup started: every {interval_hours} hours")
        return scheduler_thread

# Example usage and testing
if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create storage manager
    storage_manager = StorageManager(
        output_folder='static/outputs',
        max_age_hours=24,
        max_storage_gb=1.0  # 1GB limit for testing
    )
    
    # Get current stats
    stats = storage_manager.get_storage_stats()
    print("📊 Current Storage Stats:")
    print(f"   Files: {stats['total_files']}")
    print(f"   Size: {stats['total_size_gb']:.2f} GB")
    print(f"   Oldest file: {stats['oldest_file_hours']:.1f} hours")
    print(f"   Files over 24h: {stats['files_over_24h']}")
    print(f"   Storage usage: {stats['storage_usage_percent']:.1f}%")
    
    # Run cleanup
    print("\n🧹 Running smart cleanup...")
    result = storage_manager.smart_cleanup()
    print(f"   Deleted: {result['total_deleted']} files")
    print(f"   Freed: {result['total_freed_mb']:.1f} MB")
    print(f"   Final size: {result['final_size_gb']:.2f} GB")