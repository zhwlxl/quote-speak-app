import os
import re
from datetime import datetime, timedelta

def validate_input(form_data, config):
    """Validate user input"""
    text = form_data.get('text', '').strip()
    title = form_data.get('title', '').strip()
    
    if not text or not title:
        return "Text and title are required"
    
    if len(text) > config.get('MAX_TEXT_LENGTH', 2000):
        return f"Text too long (max {config.get('MAX_TEXT_LENGTH', 2000)} characters)"
    
    if len(title) > config.get('MAX_TITLE_LENGTH', 100):
        return f"Title too long (max {config.get('MAX_TITLE_LENGTH', 100)} characters)"
    
    # Basic content filtering
    if re.search(r'[<>"\']', text + title):
        return "Invalid characters in input"
    
    return None

def cleanup_old_files(directory, keep_count=10, max_age_hours=24):
    """Clean up old generated files to save disk space"""
    try:
        if not os.path.exists(directory):
            return
            
        files = []
        for filename in os.listdir(directory):
            if filename.endswith(('.mp4', '.png', '.mp3')):
                filepath = os.path.join(directory, filename)
                try:
                    stat = os.stat(filepath)
                    files.append((filepath, stat.st_mtime))
                except:
                    continue
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove files beyond keep_count
        for filepath, mtime in files[keep_count:]:
            try:
                os.remove(filepath)
                print(f"Cleaned up old file: {os.path.basename(filepath)}")
            except:
                pass
        
        # Remove files older than max_age_hours
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        for filepath, mtime in files[:keep_count]:  # Check even kept files for age
            if mtime < cutoff_time:
                try:
                    os.remove(filepath)
                    print(f"Cleaned up old file: {os.path.basename(filepath)}")
                except:
                    pass
                    
    except Exception as e:
        print(f"Cleanup error: {e}")

def get_file_size_mb(filepath):
    """Get file size in MB"""
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    return filename