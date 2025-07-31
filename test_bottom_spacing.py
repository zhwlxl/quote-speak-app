#!/usr/bin/env python3
"""
Test bottom spacing to ensure text doesn't touch borders
"""

import os
from dotenv import load_dotenv
from video_generator import VideoGenerator

# Load environment
load_dotenv()

def test_bottom_spacing():
    print("🧪 Testing Bottom Spacing and Border Buffer...")
    
    # Test configuration
    config = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'UPLOAD_FOLDER': 'static/outputs'
    }
    
    # Create video generator
    video_gen = VideoGenerator(config)
    
    # Test cases with different content lengths
    test_cases = [
        {
            'name': 'Maximum Content Test',
            'title': 'This is a Very Long Title That Should Test the Maximum Title Length and Auto-Sizing Feature',
            'text': '''This is an extremely long text that will push the boundaries of the content area to test the bottom spacing functionality. The text should automatically adjust its font size to ensure it fits within the card boundaries while maintaining proper spacing from all edges.

This is a second paragraph that adds even more content to test the multi-paragraph spacing and ensure that the bottom margin is properly maintained even with maximum content.

This third paragraph should further test the system's ability to handle large amounts of text while preserving the visual integrity and proper spacing from the card borders.

Finally, this fourth paragraph represents the maximum amount of content we want to test to ensure the bottom buffer space is always maintained regardless of content length.'''
        },
        {
            'name': 'Medium Content Test',
            'title': 'Medium Length Title Test',
            'text': '''This is a medium-length text that should fit comfortably within the card boundaries with proper spacing.

This second paragraph tests the paragraph spacing functionality while ensuring adequate bottom margin.'''
        },
        {
            'name': 'Minimal Content Test',
            'title': 'Short Title',
            'text': 'Short text to test minimum spacing requirements.'
        }
    ]
    
    print("Testing different content lengths for proper bottom spacing...\n")
    
    for i, test_case in enumerate(test_cases):
        print(f"   Testing {test_case['name']}...")
        
        try:
            image_path = os.path.join(config['UPLOAD_FOLDER'], f'spacing_test_{i+1}.png')
            
            # Generate image
            video_gen.create_text_image(
                test_case['text'],
                test_case['title'],
                image_path,
                'purple_blue',  # color template
                'roboto',       # title font
                'roboto'        # body font
            )
            
            if os.path.exists(image_path):
                print(f"   ✅ {test_case['name']} - Image generated successfully")
                print(f"      Title length: {len(test_case['title'])} chars")
                print(f"      Text length: {len(test_case['text'])} chars")
                print(f"      Saved to: {image_path}")
            else:
                print(f"   ❌ {test_case['name']} - Failed to generate image")
                return False
                
        except Exception as e:
            print(f"   ❌ {test_case['name']} - Error: {e}")
            return False
        
        print()
    
    print("🎉 Bottom spacing test completed!")
    print("📁 Check the generated images to verify:")
    print("   1. Text doesn't touch the card borders")
    print("   2. Consistent bottom margin in all cases")
    print("   3. Proper paragraph spacing")
    print("   4. Title and body text separation")
    
    return True

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('static/outputs', exist_ok=True)
    
    success = test_bottom_spacing()
    if success:
        print("\n✅ Bottom spacing test complete!")
    else:
        print("\n❌ Bottom spacing test failed!")