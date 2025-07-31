#!/usr/bin/env python3
"""
Test memory optimization for video generation
"""

import os
import time
from dotenv import load_dotenv
from video_generator import VideoGenerator
from memory_monitor import memory_monitor, check_available_memory

# Load environment
load_dotenv()

def test_memory_optimization():
    print("🧠 Testing Memory Optimization for Video Generation...")
    
    # Test configuration
    config = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'UPLOAD_FOLDER': 'static/outputs'
    }
    
    # Create video generator
    video_gen = VideoGenerator(config)
    
    # Test cases with different content lengths to stress memory
    test_cases = [
        {
            'name': 'Short Content (Low Memory)',
            'data': {
                'text': 'Short test for memory optimization.',
                'title': 'Memory Test 1',
                'color_template': 'purple_blue',
                'title_font': 'roboto',
                'body_font': 'roboto',
                'voice_provider': 'openai',
                'voice': 'alloy',
                'voice_speed': 1.0,
                'voice_stability': 0.5
            }
        },
        {
            'name': 'Medium Content (Moderate Memory)',
            'data': {
                'text': 'This is a medium-length text that will test memory usage during video generation. It should be long enough to create a reasonable audio file but not too long to cause memory issues.',
                'title': 'Memory Test 2 - Medium Length',
                'color_template': 'sunset',
                'title_font': 'roboto',
                'body_font': 'roboto',
                'voice_provider': 'openai',
                'voice': 'nova',
                'voice_speed': 1.0,
                'voice_stability': 0.5
            }
        },
        {
            'name': 'Long Content (High Memory)',
            'data': {
                'text': '''This is a very long text that will thoroughly test the memory optimization features of the video generation system. The text is intentionally long to create a longer audio file and test how the system handles memory management during the entire video creation process.

This second paragraph adds even more content to stress test the memory management system. We want to ensure that even with longer content, the system can successfully generate videos without running out of memory.

Finally, this third paragraph represents the maximum amount of content we want to test to ensure the memory optimization works correctly even with substantial text content that results in longer audio and video files.''',
                'title': 'Memory Test 3 - Very Long Content for Stress Testing',
                'color_template': 'ocean',
                'title_font': 'roboto',
                'body_font': 'roboto',
                'voice_provider': 'openai',
                'voice': 'shimmer',
                'voice_speed': 1.0,
                'voice_stability': 0.5
            }
        }
    ]
    
    print("\n📊 Initial Memory Status:")
    initial_memory = memory_monitor.get_memory_usage()
    for key, value in initial_memory.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.1f}")
        else:
            print(f"   {key}: {value}")
    
    # Check if we have enough memory
    if not check_available_memory(500):
        print("\n⚠️ Warning: Low memory detected. Tests may fail.")
    else:
        print("\n✅ Sufficient memory available for testing.")
    
    # Test each case
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Testing {test_case['name']}...")
        
        # Monitor memory before generation
        pre_memory = memory_monitor.get_memory_usage()
        print(f"   Memory before: {pre_memory['rss_mb']:.1f}MB")
        
        try:
            # Generate video
            timestamp = int(time.time())
            base_filename = f"memory_test_{i+1}_{timestamp}"
            
            result = video_gen.generate_video(test_case['data'], base_filename)
            
            # Monitor memory after generation
            post_memory = memory_monitor.get_memory_usage()
            memory_increase = post_memory['rss_mb'] - pre_memory['rss_mb']
            
            print(f"   Memory after: {post_memory['rss_mb']:.1f}MB (+{memory_increase:.1f}MB)")
            
            if result['success']:
                print(f"   ✅ {test_case['name']} - Video generated successfully")
                
                # Check file size
                video_path = result['video_path']
                if os.path.exists(video_path):
                    file_size_mb = os.path.getsize(video_path) / (1024 ** 2)
                    print(f"      Video size: {file_size_mb:.2f}MB")
                    print(f"      Video path: {video_path}")
            else:
                print(f"   ❌ {test_case['name']} - Failed: {result['error']}")
                
        except Exception as e:
            print(f"   ❌ {test_case['name']} - Exception: {e}")
        
        # Force cleanup between tests
        print("   🧹 Cleaning up memory...")
        memory_monitor.force_cleanup()
        
        # Wait a moment between tests
        time.sleep(2)
    
    # Final memory status
    print("\n📊 Final Memory Status:")
    final_memory = memory_monitor.get_memory_usage()
    for key, value in final_memory.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.1f}")
        else:
            print(f"   {key}: {value}")
    
    # Calculate total memory change
    total_change = final_memory['rss_mb'] - initial_memory['rss_mb']
    print(f"\n📈 Total Memory Change: {total_change:+.1f}MB")
    
    if abs(total_change) < 50:  # Less than 50MB change is good
        print("✅ Memory optimization working well - minimal memory leak")
    else:
        print("⚠️ Significant memory change detected - may need further optimization")
    
    print("\n🎉 Memory optimization test completed!")

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('static/outputs', exist_ok=True)
    
    test_memory_optimization()