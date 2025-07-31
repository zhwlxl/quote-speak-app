import os
import gc
from PIL import Image, ImageDraw, ImageFont
try:
    from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
except ImportError:
    # Fallback for different moviepy versions
    from moviepy import AudioFileClip, ImageClip, CompositeVideoClip
from voice_providers import get_voice_provider
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
        """Find optimal font size that fits within constraints"""
        font_size = initial_size
        min_size = 20
        
        while font_size >= min_size:
            font = self.get_font(font_name, font_size)
            lines = self.wrap_text(text, font, max_width)
            
            # Calculate total height
            total_height = 0
            for line in lines:
                if line.strip():
                    line_bbox = font.getbbox(line)
                    total_height += line_bbox[3] - line_bbox[1] + 5
            
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
        
        # Auto-adjust font sizes to fit content
        max_title_height = 200
        max_body_height = 800
        
        title_size = self.get_optimal_font_size(title, title_font_key, max_text_width, max_title_height, 120)
        body_size = self.get_optimal_font_size(text, body_font_key, max_text_width, max_body_height, 60)
        
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
        
        content_height += body_height + card_padding
        
        # Create image
        card_height = max(content_height, 600)  # Minimum height
        image_width = card_width + (2 * card_margin)
        image_height = card_height + (2 * card_margin)
        
        image = self.create_gradient_background(image_width, image_height, color_template)
        
        # Create card with transparency
        card = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 240))
        image.paste(card, (card_margin, card_margin), card)
        
        # Draw text
        draw = ImageDraw.Draw(image)
        text_color = color_template.text_color
        
        # Draw title
        title_x = card_margin + card_padding
        title_y = card_margin + card_padding
        
        for line in title_lines:
            draw.text((title_x, title_y), line, font=title_font, fill=text_color)
            line_bbox = title_font.getbbox(line)
            title_y += line_bbox[3] - line_bbox[1] + 10
        
        # Draw body text
        text_x = card_margin + card_padding
        text_y = card_margin + card_padding + title_height + 80
        
        for line in text_lines:
            if line:  # Skip empty lines
                draw.text((text_x, text_y), line, font=body_font, fill=text_color)
                line_bbox = body_font.getbbox(line)
                text_y += line_bbox[3] - line_bbox[1] + 20
            else:
                text_y += 30  # Space between paragraphs
        
        image.save(output_path, 'PNG', quality=95, optimize=True)
        return output_path
    
    def create_video(self, image_path, audio_path, output_path):
        try:
            audio = AudioFileClip(audio_path)
            image = ImageClip(image_path).with_duration(audio.duration)
            
            final_video = CompositeVideoClip([image]).with_audio(audio)
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                bitrate="800k",  # Optimized bitrate
                audio_bitrate="128k"
            )
            
            # Cleanup
            audio.close()
            image.close()
            final_video.close()
            
            return True
        except Exception as e:
            print(f"Video creation error: {e}")
            return False
        finally:
            # Force garbage collection
            gc.collect()
    
    def generate_video(self, data, base_filename):
        try:
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