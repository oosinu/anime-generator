"""
Illustration Generator
Shared library for AI image generation in comics
Supports:
- Alibaba Cloud Dashscope Tongyi Wanxiang
- Doubao Seedream (Volcengine)
Select via keywords: 【豆包】 or 【阿里】
"""

import os
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
from typing import Optional, Dict
import json

import os
from pathlib import Path

class IllustrationGenerator:
    """Base illustration generator class that supports multiple providers"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Load config from config.json"""
        if config_path is None:
            # Default config location
            config_path = Path('D:/software/anime/comic-generator/config.json')
        elif not Path(config_path).is_absolute():
            config_path = Path.cwd() / config_path
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.default_provider = self.config.get('default_provider', 'doubao')
        self.providers = self.config.get('providers', {})
        
        # For backward compatibility with old config format
        if 'model' in self.config and 'providers' not in self.config:
            self.providers['alibaba'] = {
                'model': self.config.get('model', 'wanx-v1'),
                'api_key': self.config.get('api_key'),
                'api_base': self.config.get('api_base'),
                'dimensions': self.config.get('dimensions', {
                    "3:4": "768*1152",
                    "9:16": "720*1280",
                    "16:9": "1280*720",
                    "1:1": "1024*1024",
                })
            }
            self.default_provider = 'alibaba'
    
    def detect_provider(self, prompt: str) -> str:
        """Detect provider from keywords in prompt: 【豆包】 or 【阿里】"""
        if '【豆包】' in prompt or '豆包' in prompt:
            return 'doubao'
        elif '【阿里】' in prompt or '阿里' in prompt:
            return 'alibaba'
        return self.default_provider
    
    def clean_prompt(self, prompt: str) -> str:
        """Remove provider keywords from prompt"""
        prompt = prompt.replace('【豆包】', '').replace('【阿里】', '').replace('豆包', '').replace('阿里', '')
        return prompt.strip()
    
    def generate_and_save(self, prompt: str, output_path: Path, aspect_ratio: str = "3:4") -> Path:
        """Generate image using detected provider and save to file"""
        provider_name = self.detect_provider(prompt)
        prompt = self.clean_prompt(prompt)
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not configured in config.json")
        
        provider_config = self.providers[provider_name]
        print(f"  Using provider: {provider_name}, model: {provider_config['model']}")
        
        if provider_name == 'alibaba':
            return self._generate_alibaba(prompt, output_path, aspect_ratio, provider_config)
        elif provider_name == 'doubao':
            return self._generate_doubao(prompt, output_path, aspect_ratio, provider_config)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def _generate_alibaba(self, prompt: str, output_path: Path, aspect_ratio: str, config: dict) -> Path:
        """Generate using Alibaba Cloud Dashscope Tongyi Wanxiang"""
        api_key = config.get('api_key') or os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable or api_key in config is required")
        
        model = config.get('model', 'wanx-v1')
        dimensions = config.get('dimensions', {
            "3:4": "768*1024",
            "4:3": "1024*768",
            "16:9": "1024*576",
            "1:1": "1024*1024",
        })
        size = dimensions.get(aspect_ratio, dimensions["3:4"])
        print(f"  Generating with size={size}...")

        rsp = ImageSynthesis.call(
            api_key=api_key,
            model=model,
            prompt=prompt,
            n=1,
            size=size
        )
        
        if rsp.status_code != HTTPStatus.OK:
            error_msg = f"Generation failed: status_code={rsp.status_code}, code={rsp.code}, message={rsp.message}"
            print(f"  {error_msg}")
            if hasattr(rsp, 'output'):
                print(f"  Output: {rsp.output}")
            raise Exception(error_msg)
        
        if not hasattr(rsp.output, 'results') or rsp.output.results is None or len(rsp.output.results) == 0:
            error_msg = f"No results returned: output={rsp.output}"
            print(f"  {error_msg}")
            raise Exception(error_msg)
        
        # Save first image
        result = rsp.output.results[0]
        file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        
        response = requests.get(result.url)
        response.raise_for_status()
        
        with open(output_path, 'wb+') as f:
            f.write(response.content)
        
        print(f"  Saved to {output_path}")
        return output_path
    
    def _generate_doubao(self, prompt: str, output_path: Path, aspect_ratio: str, config: dict) -> Path:
        """Generate using Doubao Seedream (Volcengine)"""
        # Get API key from environment or config
        api_key = config.get('api_key') or os.getenv('VOLCENGINE_API_KEY') or os.getenv('ARK_API_KEY')
        if not api_key:
            # Try to get from OpenClaw config if available
            api_key = self._get_volcengine_api_key_from_openclaw()
        if not api_key:
            raise ValueError("VOLCENGINE_API_KEY environment variable or api_key in config is required for Doubao")
        
        model = config.get('model', 'doubao-seedream-4-0-250828')
        api_base = config.get('api_base', 'https://ark.cn-beijing.volces.com/api/v3/images/generations')
        dimensions = config.get('dimensions', {
            "3:4": "768x1024",
            "4:3": "1024x768",
            "16:9": "1280x720",
            "1:1": "1024x1024",
        })
        size = dimensions.get(aspect_ratio, dimensions["3:4"])
        width, height = size.split('x')
        print(f"  Generating with size={size}...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "prompt": prompt,
            "width": int(width),
            "height": int(height),
            "n": 1
        }
        
        response = requests.post(api_base, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if 'data' not in result or len(result['data']) == 0:
            error_msg = f"No results returned: {result}"
            print(f"  {error_msg}")
            raise Exception(error_msg)
        
        # Get image URL
        image_url = result['data'][0].get('url')
        if not image_url:
            error_msg = f"No image URL in response: {result}"
            print(f"  {error_msg}")
            raise Exception(error_msg)
        
        # Download and save
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        with open(output_path, 'wb+') as f:
            f.write(img_response.content)
        
        print(f"  Saved to {output_path}")
        return output_path
    
    def _get_volcengine_api_key_from_openclaw(self) -> Optional[str]:
        """Try to get API key from OpenClaw config"""
        try:
            openclaw_config_path = Path.home() / '.openclaw' / 'openclaw.json'
            if openclaw_config_path.exists():
                with open(openclaw_config_path, 'r', encoding='utf-8') as f:
                    oc_config = json.load(f)
                providers = oc_config.get('models', {}).get('providers', {})
                if 'volcengine-plan' in providers:
                    api_key = providers['volcengine-plan'].get('apiKey')
                    if api_key and api_key != '__OPENCLAW_REDACTED__':
                        return api_key
        except Exception:
            pass
        return None

class ComicIllustrationGenerator(IllustrationGenerator):
    """Comic-specific illustration generator"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.style_prefixes = {
            'classic': 'classic ligne claire comic style, clear lines, flat colors, ',
            'ohmsha': 'Japanese shoujo tutorial manga style, Doraemon style similar, clean simple lines, ',
            'dramatic': 'dramatic high contrast comic style, strong shadows, high contrast, ',
            'warm': 'warm soft comic style, soft colors, gentle shading, ',
            'sepia': 'vintage sepia tone comic, old fashioned, retro, ',
            'vibrant': 'vibrant colorful comic, bright saturated colors, lively, ',
            'realistic': 'realistic comic style, detailed shading, realistic proportions, ',
            'wuxia': 'Chinese ink painting wuxia style, ink wash painting, brush strokes, ',
            'shoujo': 'shoujo manga style, delicate lines, soft coloring, bokeh, sparkles, ',
        }
    
    def build_comic_prompt(self, panel_description: str, style: str, character_refs: Optional[Dict] = None) -> str:
        """Build a complete comic panel prompt"""
        prefix = self.style_prefixes.get(style, self.style_prefixes['classic'])
        base_prompt = prefix + panel_description
        base_prompt += ', masterpiece, best quality, comic panel'
        
        if character_refs:
            # Add character consistency hints
            for char, ref in character_refs.items():
                base_prompt += f', {char}: {ref}'
        
        return base_prompt
