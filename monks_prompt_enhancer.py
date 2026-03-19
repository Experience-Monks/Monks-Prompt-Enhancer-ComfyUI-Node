import pathlib

import numpy as np
from PIL import Image
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Load system prompts from .md files
# ---------------------------------------------------------------------------

_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"

# Subfolder name for each image generation model
IMAGE_GENERATION_MODELS = {
    "Gemini Nano Banana": "nano_banana",
    "FLUX.2 Klein": "flux_klein",
}

PURPOSES = ["Text to Image", "Image Editing", "Multi Image Fusion"]

_PROMPT_FILENAMES = {
    "Text to Image": "text_to_image.md",
    "Image Editing": "image_editing.md",
    "Multi Image Fusion": "multi_image_fusion.md",
}


def _load_prompt(subfolder: str, filename: str) -> str:
    path = _PROMPTS_DIR / subfolder / filename
    return path.read_text(encoding="utf-8").strip()


# Nested dict: SYSTEM_PROMPTS[image_generation_model][purpose] -> system prompt string
SYSTEM_PROMPTS = {
    model_name: {
        purpose: _load_prompt(subfolder, _PROMPT_FILENAMES[purpose])
        for purpose in PURPOSES
    }
    for model_name, subfolder in IMAGE_GENERATION_MODELS.items()
}

MODEL_IDS = {
    "Gemini Flash 2.5": "gemini-2.5-flash",
}

NODE_NAME = "Monks Image Generation Prompt Enhancer"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tensor_to_pil(tensor) -> Image.Image:
    """Convert a ComfyUI IMAGE tensor (B, H, W, C) float32 to a PIL image."""
    # Take the first image in the batch
    array = tensor[0].cpu().numpy()
    array = (array * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(array)


# ---------------------------------------------------------------------------
# Node definition
# ---------------------------------------------------------------------------

class MonksPromptEnhancer:
    """ComfyUI custom node that enhances prompts via the Gemini API."""

    DESCRIPTION = (
        "Uses the Gemini API to rewrite a raw prompt into one optimised for a specific image generation model and workflow.\n"
        "\n"
        "Select the Target Image Generation Model to apply the right prompting strategy:\n"
        "  • Gemini Nano Banana — narrative prose structured around subject, setting, lighting, and atmosphere.\n"
        "  • FLUX.2 Klein — flowing descriptive prose (no keyword lists); concise action-oriented edits for img2img; simple explicit references for multi-image composition.\n"
        "\n"
        "Select the Purpose to match your workflow:\n"
        "  • Text to Image — expands a raw idea into a detailed, model-ready prompt.\n"
        "  • Image Editing — strips out base-image descriptions and returns only the transformational action.\n"
        "  • Multi Image Fusion — produces a minimal explicit reference prompt (e.g. 'change image 1 to match the style of image 2').\n"
        "\n"
        "Connect a Reference Image (optional) to include it in the Gemini call as visual context."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "api_key": ("STRING", {"default": "", "password": True}),
                "prompt_generation_model": (list(MODEL_IDS.keys()),),
                "target_image_generation_model": (list(IMAGE_GENERATION_MODELS.keys()),),
                "purpose": (PURPOSES,),
            },
            "optional": {
                "reference_image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "enhance"
    CATEGORY = "@Gemini AI/TextGen"
    OUTPUT_NODE = False

    def enhance(
        self,
        prompt: str,
        api_key: str,
        prompt_generation_model: str,
        target_image_generation_model: str,
        purpose: str,
        reference_image=None,
    ) -> tuple[str]:
        if not api_key.strip():
            raise ValueError(f"[{NODE_NAME}] API key is required.")
        if not prompt.strip():
            raise ValueError(f"[{NODE_NAME}] Prompt cannot be empty.")

        system_prompt = SYSTEM_PROMPTS[target_image_generation_model][purpose]
        model_id = MODEL_IDS[prompt_generation_model]

        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(
            model_name=model_id,
            system_instruction=system_prompt,
        )

        if reference_image is not None:
            pil_image = _tensor_to_pil(reference_image)
            content = [pil_image, prompt]
        else:
            content = prompt

        response = gemini_model.generate_content(content)

        if not response.text:
            raise RuntimeError(
                f"[{NODE_NAME}] Gemini returned an empty response. "
                "Check your API key, quota, or prompt content."
            )

        return (response.text.strip(),)


# ---------------------------------------------------------------------------
# ComfyUI registration
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "MonksPromptEnhancer": MonksPromptEnhancer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MonksPromptEnhancer": "Monks Image Generation Prompt Enhancer",
}
