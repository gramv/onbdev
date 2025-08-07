#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont

# Create a simple voided check image
img = Image.new('RGB', (400, 200), color='white')
draw = ImageDraw.Draw(img)

# Draw "VOID" text
draw.text((150, 80), "VOID", fill='red', font=None)
draw.text((50, 30), "Test Bank", fill='black')
draw.text((50, 150), "Account: ****1234", fill='black')

# Save as JPEG
img.save('test_voided_check.jpg')
print("Created test_voided_check.jpg")