import os
import gc
from PIL import Image, ImageDraw, ImageFont
try:
    from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
except ImportError:
    # Fallback for different moviepy versions
    from moviepy import AudioFileClip, ImageClip, CompositeVideoClip
from voice_providers import get_voice_provider
from memory_monitor import memory_monitor, check_available_memory, get_memory_safe_settings
from typing import NamedTuple, Tuple

class ColorTemplate(NamedTuple):
    name: str
    gradient_start: Tuple[int, int, int]
    gradient_end: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    card_color: str = 'white'

COLOR_TEMPLATES = {
    'purple_blue': ColorTemplate('Purple to Blue', (138, 43, 226), (100, 83, 246), (0, 0, 0)),
    'sunset': ColorTemplate('Sunset', (255, 128, 8), (255, 200, 55), (0, 0, 0)),
    'ocean': ColorTemplate('Ocean', (0, 119, 182), (3, 169, 244), (255, 255, 255)),
    'forest': ColorTemplate('Forest', (34, 139, 34), (154, 205, 50), (255, 255, 255)),
    'dark': ColorTemplate('Dark', (28, 28, 28), (64, 64, 64), (255, 255, 255))
}

class VideoGenerator:
    def __init__(self, config):
        self.config = config
        self.fonts_dir = os.path.join(os.path.dirname(__file__), 'static', 'fonts')
    
    def create_gradient_background(self, width, height, color_template):
        background = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(background)
        
        start_color = color_template.gradient_start
        end_color = color_template.gradient_end
        
        for x in range(width):
            progress = x / width
            r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
            for y in range(height):
                draw.point((x, y), (r, g, b))
        
        return background
    
    def get_font(self, font_name, size):
        font_paths = {
            'msyh': os.path.join(self.fonts_dir, 'MSYH.TTC'),
            'roboto': os.path.join(self.fonts_dir, 'Roboto-Regular.ttf'),
            'vera': os.path.join(self.fonts_dir, 'Vera.ttf'),
            'wqy': os.path.join(self.fonts_dir, 'wqy-zenhei.ttc')
        }
        
        font_path = font_paths.get(font_name)
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Font loading error for {font_name}: {e}")
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width with improved handling"""
        if not text.strip():
            return ['']
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed max width
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            test_width = font.getbbox(test_text)[2]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # If current line has words, save it and start new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, break it down
                    if font.getbbox(word)[2] > max_width:
                        # Break long word into smaller parts
                        chars = list(word)
                        current_chars = []
                        for char in chars:
                            test_chars = current_chars + [char]
                            test_text = ''.join(test_chars)
                            if font.getbbox(test_text)[2] <= max_width:
                                current_chars.append(char)
                            else:
                                if current_chars:
                                    lines.append(''.join(current_chars))
                                current_chars = [char]
                        if current_chars:
                            current_line = [''.join(current_chars)]
                    else:
                        current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else ['']
    
    def get_optimal_font_size(self, text, font_name, max_width, max_height, initial_size=60):
        """Find optimal font size that fits within constraints with bottom buffer"""
        font_size = initial_size
        min_size = 20
        bottom_buffer = 30  # Extra space at bottom to prevent touching border
        
        while font_size >= min_size:
            font = self.get_font(font_name, font_size)
            lines = self.wrap_text(text, font, max_width)
            
            # Calculate total height with proper line spacing
            total_height = 0
            for i, line in enumerate(lines):
                if line.strip():
                    line_bbox = font.getbbox(line)
                    line_height = line_bbox[3] - line_bbox[1]
                    total_height += line_height
                    # Add line spacing (except for last line)
                    if i < len(lines) - 1:
                        total_height += 8
            
            # Add bottom buffer to ensure space from border
            total_height += bottom_buffer
            
            if total_height <= max_height:
                return font_size
            
            font_size -= 5
        
        return min_size

    def create_text_image(self, text, title, output_path, color_template_key, title_font_key, body_font_key):
        color_template = COLOR_TEMPLATES.get(color_template_key, COLOR_TEMPLATES['purple_blue'])
        
        # Image dimensions
        card_width = 1080
        card_margin = 60
        card_padding = 100
        max_text_width = card_width - (2 * card_padding)
        
        # Calculate available space for content with proper margins
        available_height = 1200  # Base card height
        title_space = 200
        title_body_gap = 60
        bottom_margin = 50  # Ensure space at bottom
        
        # Calculate available space for body text
        body_space = available_height - title_space - title_body_gap - bottom_margin - (2 * card_padding)
        
        # Auto-adjust font sizes to fit content
        title_size = self.get_optimal_font_size(title, title_font_key, max_text_width, title_space, 120)
        body_size = self.get_optimal_font_size(text, body_font_key, max_text_width, body_space, 60)
        
        title_font = self.get_font(title_font_key, title_size)
        body_font = self.get_font(body_font_key, body_size)
        
        # Calculate content layout
        content_height = card_padding
        
        # Title height calculation
        title_lines = self.wrap_text(title, title_font, max_text_width)
        title_height = 0
        for line in title_lines:
            if line.strip():
                line_bbox = title_font.getbbox(line)
                title_height += line_bbox[3] - line_bbox[1] + 5
        
        content_height += title_height + 40  # Space after title
        
        # Body text height calculation
        text_lines = []
        paragraphs = text.split('\n\n') if '\n\n' in text else [text]
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                para_lines = self.wrap_text(paragraph, body_font, max_text_width)
                text_lines.extend(para_lines)
                # Add paragraph spacing (except for last paragraph)
                if i < len(paragraphs) - 1:
                    text_lines.append('')
        
        body_height = 0
        for line in text_lines:
            if line.strip():
                line_bbox = body_font.getbbox(line)
                body_height += line_bbox[3] - line_bbox[1] + 8
            else:
                body_height += 25  # Paragraph spacing
        
        content_height += body_height + card_padding + 30  # Extra bottom buffer
        
        # Create image with proper minimum height
        card_height = max(content_height, 700)  # Increased minimum height
        image_width = card_width + (2 * card_margin)
        image_height = card_height + (2 * card_margin)
        
        image = self.create_gradient_background(image_width, image_height, color_template)
        
        # Create card with transparency
        card = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 240))
        image.paste(card, (card_margin, card_margin), card)
        
        # Draw text
        draw = ImageDraw.Draw(image)
        text_color = color_template.text_color
        
        # Draw title with consistent spacing
        title_x = card_margin + card_padding
        title_y = card_margin + card_padding
        
        for i, line in enumerate(title_lines):
            if line.strip():
                draw.text((title_x, title_y), line, font=title_font, fill=text_color)
                line_bbox = title_font.getbbox(line)
                line_height = line_bbox[3] - line_bbox[1]
                title_y += line_height + (8 if i < len(title_lines) - 1 else 0)
        
        # Draw body text with proper spacing from title
        text_x = card_margin + card_padding
        text_y = card_margin + card_padding + title_height + 60  # Consistent gap
        
        for i, line in enumerate(text_lines):
            if line.strip():  # Regular text line
                draw.text((text_x, text_y), line, font=body_font, fill=text_color)
                line_bbox = body_font.getbbox(line)
                line_height = line_bbox[3] - line_bbox[1]
                text_y += line_height + 8  # Consistent line spacing
            else:  # Empty line (paragraph break)
                text_y += 25  # Paragraph spacing
        
        # Verify we have bottom margin (for debugging)
        final_text_y = text_y
        bottom_space = card_height - (final_text_y - card_margin)
        if bottom_space < 30:
            print(f"Warning: Only {bottom_space}px bottom space remaining")
        
        # Save with memory optimization
        image.save(output_path, 'PNG', quality=85, optimize=True)
        
        # Clear image from memory immediately
        del image
        gc.collect()
        
        return output_path
    
    @memory_monitor.memory_limit_decorator
    def create_video(self, image_path, audio_path, output_path):
        """Create video with optimized memory management"""
        
        # Check available memory before starting
        if not check_available_memory(300):  # Need at least 300MB
            print("Warning: Low memory detected, using optimized settings")
        
        # Get memory-safe settings
        memory_usage = memory_monitor.get_memory_usage()
        settings = get_memory_safe_settings(memory_usage['available_mb'])
        audio = None
        image = None
        final_video = None
        
        try:
            # Load audio first to get duration
            audio = AudioFileClip(audio_path)
            audio_duration = audio.duration
            
            # Limit audio duration to prevent memory issues
            max_duration = 300  # 5 minutes max
            if audio_duration > max_duration:
                audio = audio.subclipped(0, max_duration)
                audio_duration = max_duration
            
            # Create image clip with duration and memory-safe resolution
            image = ImageClip(image_path, duration=audio_duration)
            
            # Apply memory-safe resolution
            target_height = settings['resolution'][1]
            if target_height < 1080:  # Only resize if we need to reduce resolution
                image = image.resize(height=target_height)
            
            # Reduce image quality to save memory
            image = image.with_fps(settings['fps'])
            
            # Create video with memory-optimized settings
            final_video = CompositeVideoClip([image])
            final_video = final_video.with_audio(audio)
            
            # Write video with memory-efficient settings
            final_video.write_videofile(
                output_path,
                fps=settings['fps'],
                codec="libx264",
                audio_codec="aac",
                bitrate=settings['video_bitrate'],
                audio_bitrate=settings['audio_bitrate'],
                temp_audiofile="temp_audio.m4a",
                remove_temp=True,
                threads=settings['threads'],
                preset=settings['preset'],
                ffmpeg_params=["-movflags", "+faststart"]
            )
            
            return True
            
        except MemoryError as e:
            print(f"Memory error during video creation: {e}")
            # Try with ultra-low memory settings
            return self._create_video_low_memory(image_path, audio_path, output_path)
        except Exception as e:
            print(f"Video creation error: {e}")
            # Try with fallback method
            return self._create_video_fallback(image_path, audio_path, output_path)
        finally:
            # Explicit cleanup in reverse order
            if final_video:
                try:
                    final_video.close()
                    del final_video
                except:
                    pass
            
            if image:
                try:
                    image.close()
                    del image
                except:
                    pass
            
            if audio:
                try:
                    audio.close()
                    del audio
                except:
                    pass
            
            # Force garbage collection
            gc.collect()
            
            # Clean up any temporary files
            temp_files = ["temp_audio.m4a", "temp_audio.wav"]
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
    
    def _create_video_low_memory(self, image_path, audio_path, output_path):
        """Ultra-low memory fallback method"""
        print("Attempting low-memory video creation...")
        
        try:
            # Use ffmpeg directly for minimal memory usage
            import subprocess
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', image_path,
                '-i', audio_path,
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-crf', '28',  # Higher compression
                '-c:a', 'aac', '-b:a', '64k',
                '-shortest', '-pix_fmt', 'yuv420p',
                '-vf', 'scale=854:480',  # Force 480p
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                print("Low-memory video creation successful")
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Low-memory fallback failed: {e}")
            return False
    
    def _create_video_fallback(self, image_path, audio_path, output_path):
        """Simple fallback method using basic MoviePy"""
        print("Attempting fallback video creation...")
        
        audio = None
        image = None
        video = None
        
        try:
            # Load with minimal settings
            audio = AudioFileClip(audio_path)
            
            # Limit duration
            if audio.duration > 60:  # Max 1 minute for fallback
                audio = audio.subclipped(0, 60)
            
            # Create simple image clip
            image = ImageClip(image_path, duration=audio.duration)
            image = image.resize(height=480)  # Force low resolution
            
            # Create video
            video = image.with_audio(audio)
            
            # Write with minimal settings
            video.write_videofile(
                output_path,
                fps=20,
                codec="libx264",
                audio_codec="aac",
                bitrate="300k",
                audio_bitrate="64k",
                preset="ultrafast",
                threads=1
            )
            
            return True
            
        except Exception as e:
            print(f"Fallback method failed: {e}")
            return False
        finally:
            # Cleanup
            for obj in [video, image, audio]:
                if obj:
                    try:
                        obj.close()
                        del obj
                    except:
                        pass
            gc.collect()
    
    @memory_monitor.memory_limit_decorator
    def generate_video(self, data, base_filename):
        try:
            # Check memory before starting
            if not check_available_memory(400):
                return {'success': False, 'error': 'Insufficient memory for video generation. Please try again later.'}
            # File paths
            image_path = os.path.join(self.config['UPLOAD_FOLDER'], f"{base_filename}.png")
            audio_path = os.path.join(self.config['UPLOAD_FOLDER'], f"{base_filename}.mp3")
            video_path = os.path.join(self.config['UPLOAD_FOLDER'], f"{base_filename}.mp4")
            
            # Generate image
            self.create_text_image(
                data['text'], data['title'], image_path,
                data['color_template'], data['title_font'], data['body_font']
            )
            
            # Generate audio
            provider = get_voice_provider(data['voice_provider'], self.config)
            if not provider or not provider.is_available():
                return {'success': False, 'error': f'Voice provider {data["voice_provider"]} not available'}
            
            voice_params = {
                'speed': data['voice_speed'],
                'stability': data['voice_stability']
            }
            
            audio_success = provider.generate_speech(
                data['text'], data['voice'], audio_path, **voice_params
            )
            
            if not audio_success:
                return {'success': False, 'error': 'Failed to generate audio'}
            
            # Create video
            video_success = self.create_video(image_path, audio_path, video_path)
            
            if video_success:
                # Cleanup intermediate files
                try:
                    os.remove(image_path)
                    os.remove(audio_path)
                except:
                    pass
                
                return {'success': True, 'video_path': video_path}
            else:
                return {'success': False, 'error': 'Failed to create video'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}