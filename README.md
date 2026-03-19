# Nano-Banana-Monks Prompt Enhancer

A ComfyUI custom node that enhances image generation prompts using the Gemini API.

## Features

- Enhances raw prompts into detailed, model-optimized descriptions
- Three purpose-specific system prompts tuned for different workflows
- Masked API key input
- Raises errors on failure — no silent fallbacks

## Installation

1. Copy the `monks_prompt_enhancer/` folder into your `ComfyUI/custom_nodes/` directory.
2. Install the dependency:
   ```bash
   pip install google-generativeai
   ```
3. Restart ComfyUI.

The node will appear under the **Gemini AI/TextGen** category.

## Inputs

| Input | Type | Description |
|---|---|---|
| `prompt` | Text (multiline) | The raw prompt to enhance |
| `api_key` | Text (masked) | Your Google Gemini API key |
| `model` | Dropdown | Gemini model to use |
| `purpose` | Dropdown | Prompt enhancement mode |
| `reference_image` | IMAGE (optional) | Reference image passed to Gemini alongside the prompt |

## Outputs

| Output | Type | Description |
|---|---|---|
| `enhanced_prompt` | STRING | The enhanced prompt returned by Gemini |

## Purposes

### Text to Image
Rewrites the prompt as a flowing, narrative paragraph structured around subject, setting, details, lighting, atmosphere, and style — optimized for Gemini's native text-to-image generation. If a reference image is connected, Gemini uses it as a style or composition reference.

### Image Editing
Refines the prompt to clearly describe **what should change** in a reference image, using precise editing patterns (additions, removals, style transfers, multi-image compositions). Connect the image being edited as the reference image.

### Multi Image Fusion
Structures the prompt for inpainting: clearly names the target region to change and explicitly preserves everything else, using Gemini's semantic masking capabilities. Connect the base image as the reference image.

## System Prompts

Each purpose loads its system prompt from a `.md` file under `prompts/`:

```
prompts/
├── text_to_image.md
├── image_editing.md
└── multi_image_fusion.md
```

Edit these files to customize the enhancement behavior without touching the node code.

## Models

| Display name | Model ID |
|---|---|
| Gemini Flash 2.5 | `gemini-2.5-flash` |
