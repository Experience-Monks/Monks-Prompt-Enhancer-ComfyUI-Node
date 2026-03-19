import pathlib

import numpy as np
from PIL import Image
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Load system prompts from .md files
# ---------------------------------------------------------------------------

_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8").strip()


SYSTEM_PROMPTS = {
    "Text to Image": _load_prompt("text_to_image.md"),
    "Image Editing": _load_prompt("image_editing.md"),
    "Multi Image Fusion": _load_prompt("multi_image_fusion.md"),
}

MODEL_IDS = {
    "Gemini Flash 2.5": "gemini-2.5-flash",
}

NODE_NAME = "Nano-Banana-Monks Prompt Enhancer"


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

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "api_key": ("STRING", {"default": "", "password": True}),
                "model": (list(MODEL_IDS.keys()),),
                "purpose": (list(SYSTEM_PROMPTS.keys()),),
            },
            "optional": {
                "reference_image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "enhance"
    CATEGORY = "Gemini AI/TextGen"
    OUTPUT_NODE = False

    def enhance(
        self,
        prompt: str,
        api_key: str,
        model: str,
        purpose: str,
        reference_image=None,
    ) -> tuple[str]:
        if not api_key.strip():
            raise ValueError(f"[{NODE_NAME}] API key is required.")
        if not prompt.strip():
            raise ValueError(f"[{NODE_NAME}] Prompt cannot be empty.")

        system_prompt = SYSTEM_PROMPTS[purpose]
        model_id = MODEL_IDS[model]

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
    "MonksPromptEnhancer": NODE_NAME,
}
