import shutil
import os

# List of required icon files
required_icons = [
    'book.svg',
    'home.svg',
    'users.svg',
    'refresh-cw.svg',
    'file-text.svg',
    'dollar-sign.svg',
    'bell.svg',
    'calendar.svg',
    'message-square.svg',
    'user.svg',
    'edit.svg',
    'trash.svg',
    'search.png'  # Also include the search.png mentioned in book_inventory_page.py
]

# Create icons directory if it doesn't exist
os.makedirs('icons', exist_ok=True)

# Copy placeholder.svg to all required icon files
for icon in required_icons:
    if not os.path.exists(f'icons/{icon}'):
        if icon.endswith('.svg'):
            shutil.copy2('icons/placeholder.svg', f'icons/{icon}')
            print(f'Created: icons/{icon}')
        elif icon == 'search.png':
            # Create a simple search icon as SVG and convert to PNG
            with open('icons/search.svg', 'w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="11" cy="11" r="7" stroke="#94A3B8" stroke-width="2"/>
  <path d="M16 16L21 21" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
</svg>''')
            # Convert SVG to PNG (this requires cairosvg or similar library)
            try:
                import cairosvg
                cairosvg.svg2png(url='icons/search.svg', write_to='icons/search.png')
                print('Created: icons/search.png')
            except ImportError:
                print('Warning: cairosvg not installed. Install with: pip install cairosvg')
                print('Falling back to SVG for search icon')
                shutil.copy2('icons/search.svg', 'icons/search.png')

print('\nIcons setup complete. You may need to recompile the .qrc file if you want to use the icons in your application.')
print('To compile the .qrc file, run: pyrcc5 resources.qrc -o resources_rc.py')
