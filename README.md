
# anime Generator - 知识漫画生成器

将文章、教程、人物传记转换为漫画形式，支持豆包 Seedream 和阿里通义万相双模型。

## 功能特性

- 📚 **内容分析** - 自动分析内容，推荐适配的风格和布局
- 🎭 **角色生成** - 根据内容生成主角配角设计和视觉规范
- 📖 **分镜设计** - 智能分页、自动生成脚本和对话
- 🎨 **9种预设风格** - 从传统欧漫到武侠水墨全覆盖
- 📐 **6种布局** - 适配不同阅读体验
- 🔄 **后期修改** - 支持单页重生成、添加、删除
- 🤖 **双模型支持** - 默认豆包 Seedream，可通过关键字切换阿里
- 📦 **自动输出PDF** - 合并所有页面为成品

## 支持的风格

| 风格 | 说明 | 适用内容 |
|------|------|---------|
| classic | Ligne Claire 传统欧漫 | 人物传记、历史 |
| ohmsha | 日式教程漫画（哆啦A梦风） | 技术教程、科普 |
| dramatic | 戏剧性高对比 | 冲突、转折点 |
| warm | 温暖柔和 | 个人故事、成长 |
| sepia | 复古棕褐色调 | 历史、回忆 |
| vibrant | 鲜艳活泼 | 儿童内容、趣味科普 |
| realistic | 写实风格 | 商业、专业内容 |
| wuxia | 武侠水墨风 | 武侠、中国历史 |
| shoujo | 少女漫画风 | 情感、校园 |

## 支持的布局

| 布局 | 分镜数 | 说明 |
|------|-------|------|
| standard | 4-6 | 标准网格，通用 |
| cinematic | 3-4 | 电影感宽幅 |
| dense | 6-9 | 密集信息 |
| splash | 1-2 | 全页大图 |
| mixed | 3-6 | 混合大小 |
| webtoon | 3-5 | 竖向滚动（手机） |

## 模型切换

在生成命令中通过关键字控制：
- `【豆包】` - 使用豆包 Seedream 文生图（默认）
- `【阿里】` - 使用阿里通义万相

## 快速开始

```bash
# 1. 内容分析和分镜设计
/anime-generator article.md

# 生成图片（默认豆包）
/anime-generator anime/slug generate

# 3. 生成图片（指定阿里）
/anime-generator 【阿里】 anime/slug generate

# 4. 合并PDF
python utils/pdf_merge.py anime/slug/images-ch1 anime/slug/output.pdf
```

## 配置

`config.json` 结构：

```json
{
  "default_provider": "doubao",
  "providers": {
    "alibaba": {
      "model": "wanx-v1",
      "api_key": "xxx",
      "dimensions": {...}
    },
    "doubao": {
      "model": "doubao-seedream-4-0-250828",
      "api_key": "",
      "dimensions": {...}
    }
  }
}
```

- 豆包 API key 自动从 OpenClaw 配置读取
- 阿里 API key 直接配置在 `config.json`

## 作者

本地私有 skill，不公开。

## 许可证

私有
