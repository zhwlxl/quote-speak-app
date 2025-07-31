# 🚀 Start Local Test Server

## Quick Start Commands:

```bash
cd content-creation/quote_speak_app_deploy
source venv/bin/activate
python run_test_server.py
```

## Then open your browser to:
**http://localhost:5555**

## 🧪 Test Cases to Try:

### 1. Short Text Test:
- **Title**: `Short Quote`
- **Text**: `Hello world! This is a short test.`

### 2. Medium Text Test:
- **Title**: `Medium Length Quote`
- **Text**: `This is a medium length quote that should wrap nicely across multiple lines and demonstrate the text wrapping functionality.`

### 3. Long Text Test:
- **Title**: `Very Long Quote with Extended Title`
- **Text**: `This is a very long quote that will test the automatic font sizing and text wrapping features. The system should automatically adjust the font size to ensure all text fits within the card boundaries. This paragraph contains enough text to thoroughly test the wrapping and sizing functionality.`

### 4. Multi-Paragraph Test:
- **Title**: `Multi-Paragraph Quote`
- **Text**: 
```
This is the first paragraph of a multi-paragraph quote.

This is the second paragraph that should be properly spaced from the first paragraph.

And this is a third paragraph to test multiple paragraph handling.
```

### 5. Very Long Title Test:
- **Title**: `This is a Very Long Title That Should Auto-Adjust Its Font Size`
- **Text**: `Testing how the system handles long titles with automatic font adjustment.`

## ✅ What to Look For:

1. **Text Wrapping**: All text should fit within the card boundaries
2. **Font Auto-Sizing**: Long text should use smaller fonts automatically
3. **Paragraph Spacing**: Multiple paragraphs should be properly spaced
4. **Title Adjustment**: Long titles should resize to fit
5. **Visual Quality**: Text should be readable and well-formatted

## 🎨 Try Different Styles:

- **Color Templates**: Purple to Blue, Sunset, Ocean, Forest, Dark
- **Fonts**: Microsoft YaHei, WQY ZenHei, Vera, Roboto
- **Voice Options**: Different OpenAI voices (Alloy, Nova, Shimmer, etc.)

## 🛑 To Stop Server:
Press `Ctrl+C` in the terminal