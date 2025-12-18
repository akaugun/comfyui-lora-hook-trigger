import os
from aiohttp import web
import folder_paths
from server import PromptServer

WEB_DIRECTORY = "js"


def _safe_full_path_for_lora(lora_name: str):
    if not lora_name:
        return None
    try:
        p = folder_paths.get_full_path("loras", lora_name)
    except Exception:
        return None
    if not p or not isinstance(p, (str, bytes, os.PathLike)):
        return None
    return p


def _trigger_dir_from_lora_full_path(full_path):
    if not full_path:
        return None
    base, _ = os.path.splitext(full_path)
    return base if base else None


def _read_text_best_effort(path: str) -> str:
    if not path or not os.path.isfile(path):
        return ""
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except Exception:
            pass
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


@PromptServer.instance.routes.get("/lora_trigger_list")
async def lora_trigger_list(request):
    lora_name = request.rel_url.query.get("lora_name", "")
    triggers = ["NONE"]

    full_path = _safe_full_path_for_lora(lora_name)
    trigger_dir = _trigger_dir_from_lora_full_path(full_path)

    if trigger_dir and os.path.isdir(trigger_dir):
        try:
            names = []
            for fname in os.listdir(trigger_dir):
                if not isinstance(fname, str):
                    continue
                if not fname.lower().endswith(".txt"):
                    continue
                stem, _ = os.path.splitext(fname)
                if stem:
                    names.append(stem)
            for n in sorted(set(names)):
                if n not in triggers:
                    triggers.append(n)
        except Exception:
            pass

    return web.json_response({"triggers": triggers})


def _create_lora_hook_best_effort(lora_name: str, strength_model: float, strength_clip: float):
    try:
        from comfy_extras import nodes_hooks
    except Exception:
        return None

    try:
        creator = nodes_hooks.CreateHookLora()
    except Exception:
        return None

    try:
        if hasattr(creator, "create_hook"):
            return creator.create_hook(lora_name, strength_model, strength_clip)
    except Exception:
        pass

    try:
        if hasattr(creator, "run"):
            out = creator.run(lora_name, strength_model, strength_clip)
            if isinstance(out, (tuple, list)) and out:
                return out[0]
            return out
    except Exception:
        pass

    return None


class LoraTriggerWithExample:
    @classmethod
    def INPUT_TYPES(cls):
        try:
            loras = folder_paths.get_filename_list("loras")
        except Exception:
            loras = []
        if not loras:
            loras = [""]

        return {
            "required": {
                "lora_name": (loras,),
                "trigger": ("STRING", {"default": "NONE"}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("HOOK", "STRING")
    RETURN_NAMES = ("hook", "example")
    FUNCTION = "run"
    CATEGORY = "advanced/hooks"

    def _read_trigger_text(self, lora_name: str, trigger: str) -> str:
        if not trigger or trigger == "NONE":
            return ""

        full_path = _safe_full_path_for_lora(lora_name)
        trigger_dir = _trigger_dir_from_lora_full_path(full_path)
        if not trigger_dir or not os.path.isdir(trigger_dir):
            return ""

        txt_path = os.path.join(trigger_dir, f"{trigger}.txt")
        return _read_text_best_effort(txt_path).rstrip()

    def run(self, lora_name, trigger, strength_model, strength_clip):
        hook = _create_lora_hook_best_effort(lora_name, strength_model, strength_clip)
        text = self._read_trigger_text(lora_name, trigger)
        return (hook, text)


NODE_CLASS_MAPPINGS = {
    "LoraTriggerWithExample": LoraTriggerWithExample,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraTriggerWithExample": "LoRA Hook + Trigger Text",
}
