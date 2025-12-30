import os
from PIL import Image, ImageDraw, ImageFont

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_image(text, filename, size=(40, 60), bg_color=(0, 0, 0, 0), text_color=(255, 255, 255, 255)):
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Simple logic to center text roughly without external fonts if possible, 
    # but drawing default font is small. Let's try to draw a simple shape or text.
    # Since we don't know what fonts are available, we'll draw lines to form the number/text 
    # or just use default load_default().
    
    # For better visibility, let's draw a colored rectangle with the text inside
    # Actually, let's just use the default font but scale it up? No, PIL default font is bitmap.
    # We will just draw the text in top left for now, or use a large rectangle as placeholder.
    
    # Draw a border
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=text_color, width=2)
    
    # Draw text in center (approximate)
    # Using a simple cross for placeholder if text is special, but for numbers let's try.
    # Since we want it to be visible, let's fill a slight background
    draw.rectangle([2, 2, size[0]-3, size[1]-3], fill=(0, 0, 0, 50))
    
    # Draw the character
    # We'll just draw a big letter using lines or just rely on the user replacing them.
    # But to make it usable, I will try to use a basic truetype font if available, else default.
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # Get bounding box to center
    try:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        w = right - left
        h = bottom - top
    except AttributeError:
        w, h = draw.textsize(text, font=font)
        
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, font=font, fill=text_color)
    
    img.save(filename)
    print(f"Generated {filename}")

def generate_bg(filename, size=(400, 200)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a semi-transparent rounded rectangle or just a rectangle
    draw.rectangle([0, 0, size[0]-1, size[1]-1], fill=(0, 0, 0, 100), outline=(255, 255, 255, 200), width=4)
    img.save(filename)
    print(f"Generated {filename}")

def main():
    assets_dir = "assets"
    create_directory(assets_dir)
    
    # Generate 0-9
    for i in range(10):
        generate_image(str(i), os.path.join(assets_dir, f"{i}.png"))
        
    # Generate colon
    generate_image(":", os.path.join(assets_dir, "colon.png"), size=(20, 60))
    
    # Generate background
    generate_bg(os.path.join(assets_dir, "bg.png"))

if __name__ == "__main__":
    main()
