import os
from aiohttp import web
import folder_paths
from server import PromptServer

WEB_DIRECTORY = "js"


@PromptServer.instance.routes.get("/lora_trigger_list")
async def lora_trigger_list(request):
    lora_name = request.rel_url.query.get("lora_name", "")
    triggers = ["NONE"]

    if not lora_name:
        return web.json_response({"triggers": triggers})

    try:
        full_path = folder_paths.get_full_path("loras", lora_name)
    except Exception:
        return web.json_response({"triggers": triggers})

    base, _ = os.path.splitext(full_path)
    trigger_dir = base

    if os.path.isdir(trigger_dir):
        try:
            for fname in sorted(os.listdir(trigger_dir)):
                if fname.lower().endswith(".txt"):
                    name_without_ext, _ = os.path.splitext(fname)
                    if name_without_ext and name_without_ext not in triggers:
                        triggers.append(name_without_ext)
        except Exception:
            pass

    return web.json_response({"triggers": triggers})


class LoraTriggerWithExample:
    @classmethod
    def INPUT_TYPES(cls):
        loras = folder_paths.get_filename_list("loras")
        return {
            "required": {
                "lora_name": (loras,),
                "trigger": ("STRING", {"default": "NONE"}),
                "strength_model": (
                    "FLOAT",
                    {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01},
                ),
                "strength_clip": (
                    "FLOAT",
                    {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01},
                ),
            },
            "optional": {
                "prev_hooks": ("HOOKS",),
            },
        }

    RETURN_TYPES = ("HOOKS", "STRING")
    RETURN_NAMES = ("HOOKS", "example")
    FUNCTION = "run"
    CATEGORY = "advanced/hooks"

    def _read_trigger_text(self, lora_name: str, trigger: str) -> str:
        if not trigger or trigger == "NONE":
            return ""

        try:
            full_path = folder_paths.get_full_path("loras", lora_name)
        except Exception:
            return ""

        base, _ = os.path.splitext(full_path)
        txt_path = os.path.join(base, f"{trigger}.txt")

        if not os.path.exists(txt_path):
            return ""

        for enc in ("utf-8", "utf-8-sig", "cp949"):
            try:
                with open(txt_path, "r", encoding=enc, errors="ignore") as f:
                    return f.read()
            except Exception:
                continue

        return ""

    def _create_hook(self, lora_name, strength_model, strength_clip, prev_hooks):
        try:
            from comfy_extras import nodes_hooks
        except Exception:
            return None

        creator = nodes_hooks.CreateHookLora()
        result = creator.create_hook(
            lora_name=lora_name,
            strength_model=strength_model,
            strength_clip=strength_clip,
            prev_hooks=prev_hooks,
        )

        if isinstance(result, tuple) and len(result) > 0:
            return result[0]

        return result

    def run(self, lora_name, trigger, strength_model, strength_clip, prev_hooks=None):
        hook = self._create_hook(lora_name, strength_model, strength_clip, prev_hooks)
        text = self._read_trigger_text(lora_name, trigger)
        return (hook, text)


NODE_CLASS_MAPPINGS = {
    "LoraTriggerWithExample": LoraTriggerWithExample,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraTriggerWithExample": "LoRA Hook + Trigger Text",
}
