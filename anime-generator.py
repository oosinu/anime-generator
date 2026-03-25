#!/usr/bin/env python3
"""
This skill is compatible with OpenClaw. 
It is modified based on the open-source Comic Generator project, 
providing the function of converting articles, tutorials and biographies into comic format.
The image generation uses models from Alibaba Cloud and Doubao large model.
"""

import argparse
import sys
import os
import json
from pathlib import Path

from lib.illustration import ComicIllustrationGenerator

# Style definitions
STYLES = {
    'classic': 'Ligne Claire traditional European comic',
    'ohmsha': 'Japanese tutorial manga style (Doraemon like)',
    'dramatic': 'Dramatic high contrast style',
    'warm': 'Warm and soft style',
    'sepia': 'Vintage sepia tone',
    'vibrant': 'Vibrant and lively',
    'realistic': 'Realistic style',
    'wuxia': 'Chinese ink painting wuxia style',
    'shoujo': 'Japanese shoujo manga style',
}

# Layout definitions
LAYOUTS = {
    'standard': (4, 6),
    'cinematic': (3, 4),
    'dense': (6, 9),
    'splash': (1, 2),
    'mixed': (3, 6),
    'webtoon': (3, 5),
}

ASPECT_RATIOS = {
    '3:4': '3:4',
    '4:3': '4:3',
    '16:9': '16:9',
}

def load_style(style_name):
    """Load style definition from references"""
    style_file = Path(__file__).parent / 'references' / 'styles' / f'{style_name}.md'
    if style_file.exists():
        with open(style_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def load_layout(layout_name):
    """Load layout definition from references"""
    layout_file = Path(__file__).parent / 'references' / 'layouts' / f'{layout_name}.md'
    if layout_file.exists():
        with open(layout_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def analyze_content(source_path, style=None, layout=None, aspect='3:4'):
    """Step 1: Analyze content and recommend configuration"""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Auto-select based on content keywords
    if style is None:
        if any(keyword in content for keyword in ['tutorial', '入门', '指南', '教程']):
            style = 'ohmsha'
        elif any(keyword in content for keyword in ['history', '古代', '历史']):
            style = 'sepia'
        elif any(keyword in content for keyword in ['story', '成长', '个人', '故事']):
            style = 'warm'
        elif any(keyword in content for keyword in ['conflict', 'break', '突破', '冲突']):
            style = 'dramatic'
        elif any(keyword in content for keyword in ['wuxia', '武侠', '仙侠']):
            style = 'wuxia'
        elif any(keyword in content for keyword in ['campus', 'school', '情感', '青春', '校园']):
            style = 'shoujo'
        elif any(keyword in content for keyword in ['biography', '传记']):
            style = 'classic'
        else:
            style = 'classic'
    
    if layout is None:
        if any(keyword in content for keyword in ['tutorial', '入门', '指南', '教程']):
            layout = 'webtoon'
        elif any(keyword in content for keyword in ['coding', 'programming', '编程', 'AI', '技术']):
            layout = 'dense'
        elif any(keyword in content for keyword in ['history', '古代', '历史']):
            layout = 'cinematic'
        elif any(keyword in content for keyword in ['story', '成长', '个人', '故事']):
            layout = 'standard'
        elif any(keyword in content for keyword in ['conflict', 'break', '突破', '冲突']):
            layout = 'splash'
        elif any(keyword in content for keyword in ['wuxia', '武侠', '仙侠']):
            layout = 'splash'
        elif any(keyword in content for keyword in ['biography', '传记']):
            layout = 'mixed'
        else:
            layout = 'standard'
    
    return {
        'style': style,
        'layout': layout,
        'aspect': aspect,
        'content': content,
    }

def main():
    parser = argparse.ArgumentParser(description='Comic Generator - Knowledge Comic Generator')
    parser.add_argument('source', help='Source markdown file with content or comic directory for generate')
    parser.add_argument('--style', help='Comic style', choices=list(STYLES.keys()))
    parser.add_argument('--layout', help='Page layout', choices=list(LAYOUTS.keys()))
    parser.add_argument('--aspect', help='Aspect ratio', choices=list(ASPECT_RATIOS.keys()), default='3:4')
    parser.add_argument('--output', help='Output directory', default=None)
    parser.add_argument('action', nargs='?', help='Action: regenerate/add/delete/generate', default=None)
    parser.add_argument('--page', help='Page number for regenerate', type=int)
    parser.add_argument('--after', help='Page number after which to add', type=int)
    parser.add_argument('--content', help='Content for added page')
    parser.add_argument('--config', help='Path to config.json', default=None)
    
    args = parser.parse_args()
    
    # Handle generate action (generate all images from existing prompts)
    if args.action == 'generate':
        # source is comic directory
        comic_dir = Path(args.source)
        if not comic_dir.exists():
            print(f"❌ Comic directory {comic_dir} does not exist")
            sys.exit(1)
        
        # Load config and initialize generator
        gen = ComicIllustrationGenerator(args.config)
        
        # Find all prompt files
        prompts_dir = comic_dir / 'prompts-ch1'
        if not prompts_dir.exists():
            prompts_dir = comic_dir / 'prompts'
        if not prompts_dir.exists():
            print(f"❌ No prompts directory found in {comic_dir}")
            sys.exit(1)
        
        # Create images directory
        images_dir = comic_dir / 'images-ch1'
        if not images_dir.exists():
            images_dir = comic_dir / 'images'
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all prompt files sorted
        prompt_files = sorted(list(prompts_dir.glob('*.md')))
        print(f"[*] Found {len(prompt_files)} prompt files")
        print(f"[*] Generating images...")
        
        # Generate each image
        for i, prompt_file in enumerate(prompt_files):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract prompt from the file (look for code block)
            import re
            prompt_match = re.search(r'```(.*?)```', content, re.DOTALL)
            if prompt_match:
                prompt = prompt_match.group(1).strip()
            else:
                prompt = content.strip()
            
            # Output filename
            output_name = prompt_file.stem + '.png'
            output_path = images_dir / output_name
            
            print(f"  [{i+1}/{len(prompt_files)}] Generating {output_name}...")
            try:
                gen.generate_and_save(prompt, output_path, args.aspect)
                print(f"  [OK] Saved to {output_path}")
            except Exception as e:
                print(f"  [FAIL] Failed: {e}")
        
        print(f"\n[OK] All images generated in {images_dir}")
        print(f"Next step: run python utils/pdf_merge.py {images_dir} {comic_dir / (comic_dir.name + '.pdf')} to create PDF")
        return
    
    # Create output directory
    if args.output is None:
        # Extract slug from filename
        slug = Path(args.source).stem
        output_dir = Path.cwd() / 'comic' / slug
    else:
        output_dir = Path(args.output)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Content analysis
    analysis = analyze_content(args.source, args.style, args.layout, args.aspect)
    
    # Save analysis
    with open(output_dir / 'source.md', 'w', encoding='utf-8') as f:
        f.write(analysis['content'])
    
    analysis_text = f"""# Content Analysis

- Source: {args.source}
- Style: {analysis['style']} ({STYLES[analysis['style']]})
- Layout: {analysis['layout']} ({LAYOUTS[analysis['layout']][0]}-{LAYOUTS[analysis['layout']][1]} panels)
- Aspect Ratio: {analysis['aspect']}

## Content Summary

{analysis['content'][:500]}...
"""
    with open(output_dir / 'analysis.md', 'w', encoding='utf-8') as f:
        f.write(analysis_text)
    
    print(f"✅ Content analysis completed")
    print(f"   Style: {analysis['style']}")
    print(f"   Layout: {analysis['layout']}")
    print(f"   Output directory: {output_dir}")
    print("\nNext step: Create character design in characters/")

if __name__ == '__main__':
    main()
