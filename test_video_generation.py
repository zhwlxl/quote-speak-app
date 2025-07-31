#!/usr/bin/env python3
"""
Test video generation locally
"""

import os
from dotenv import load_dotenv
from video_generator import VideoGenerator
from voice_providers import get_voice_provider

# Load environment
load_dotenv()

def test_video_generation():
    print("🧪 Testing Video Generation with Auto Text Adjustment...")
    
    # Test configuration
    config = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'UPLOAD_FOLDER': 'static/outputs'
    }
    
    # Create video generator
    video_gen = VideoGenerator(config)
    
    # Test data with different text lengths
    test_cases = [
        {
            'name': 'Short Text',
            'data': {
                'text': 'This is a short test message.',
                'title': 'Short Test',
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
            'name': 'Medium Text',
            'data': {
                'text': 'This is a medium length test message that should wrap across multiple lines and demonstrate the text wrapping functionality of the quote speak application.',
                'title': 'Medium Length Test Quote',
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
            'name': 'Long Text',
            'data': {
                'text': 'This is a very long test message that will definitely require multiple lines and should test the automatic font size adjustment feature. The text wrapping algorithm should handle this gracefully and ensure that all text fits within the designated card area. This paragraph contains enough text to thoroughly test the wrapping and sizing functionality.\n\nThis is a second paragraph to test paragraph spacing and multi-paragraph handling. The system should properly separate paragraphs and maintain good visual spacing between them.',
                'title': 'Very Long Test Quote with Extended Title',
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
    
    # Test voice provider
    print("1. Testing voice provider...")
    provider = get_voice_provider('openai', config)
    if provider and provider.is_available():
        print("✅ OpenAI voice provider available")
    else:
        print("❌ OpenAI voice provider not available")
        return False
    
    # Test multiple text lengths
    print("2. Testing text auto-adjustment with different lengths...")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n   Testing {test_case['name']}...")
        test_data = test_case['data']
        
        try:
            # Generate image
            image_path = os.path.join(config['UPLOAD_FOLDER'], f'test_image_{i+1}.png')
            video_gen.create_text_image(
                test_data['text'], 
                test_data['title'], 
                image_path,
                test_data['color_template'], 
                test_data['title_font'], 
                test_data['body_font']
            )
            
            if os.path.exists(image_path):
                print(f"   ✅ {test_case['name']} image generated")
                print(f"      Text length: {len(test_data['text'])} chars")
                print(f"      Title length: {len(test_data['title'])} chars")
            else:
                print(f"   ❌ {test_case['name']} image generation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ {test_case['name']} error: {e}")
            return False
    
    # Test audio generation with medium text
    print("\n3. Testing audio generation...")
    test_data = test_cases[1]['data']  # Use medium text
    try:
        audio_path = os.path.join(config['UPLOAD_FOLDER'], 'test_audio.mp3')
        audio_success = provider.generate_speech(
            test_data['text'], 
            test_data['voice'], 
            audio_path,
            speed=test_data['voice_speed']
        )
        if audio_success and os.path.exists(audio_path):
            print("✅ Audio generated successfully")
            print(f"   Audio saved to: {audio_path}")
        else:
            print("❌ Audio generation failed")
            return False
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
        return False
    
    # Test video generation
    print("4. Testing video generation...")
    try:
        image_path = os.path.join(config['UPLOAD_FOLDER'], 'test_image_2.png')  # Use medium text image
        video_path = os.path.join(config['UPLOAD_FOLDER'], 'test_video.mp4')
        video_success = video_gen.create_video(image_path, audio_path, video_path)
        if video_success and os.path.exists(video_path):
            print("✅ Video generated successfully")
            print(f"   Video saved to: {video_path}")
            
            # Get file size
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"   Video size: {file_size:.2f} MB")
        else:
            print("❌ Video generation failed")
            return False
    except Exception as e:
        print(f"❌ Video generation error: {e}")
        return False
    
    print("\n🎉 All tests passed! Your app is ready to use.")
    print(f"📁 Generated files in: {config['UPLOAD_FOLDER']}")
    return True

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('static/outputs', exist_ok=True)
    
    success = test_video_generation()
    if success:
        print("\n✅ Local testing complete - ready for deployment!")
    else:
        print("\n❌ Local testing failed - check the errors above")