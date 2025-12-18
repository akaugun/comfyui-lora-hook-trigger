import os
from aiohttp import web
import folder_paths
from server import PromptServer

WEB_DIRECTORY = "js"


def _unwrap_single(x):
    if isinstance(x, (tuple, list)) and len(x) == 1:
        return x[0]
    return x


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
    base, _ = os.path.splitext(str(full_path))
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
                if n != "NONE":
                    triggers.append(n)
        except Exception:
            pass

    return web.json_response({"triggers": triggers})


def _combine_hooks_best_effort(prev_hooks, new_hook):
    if prev_hooks is None:
        return new_hook
    if new_hook is None:
        return prev_hooks
    try:
        from comfy_extras import nodes_hooks
    except Exception:
        return new_hook
    try:
        combiner = nodes_hooks.CombineHooks()
    except Exception:
        return new_hook

    out = None
    try:
        if hasattr(combiner, "combine"):
            out = combiner.combine(prev_hooks, new_hook)
        elif hasattr(combiner, "run"):
            out = combiner.run(prev_hooks, new_hook)
    except Exception:
        out = None

    out = _unwrap_single(out)
    return out if out is not None else new_hook


def _create_lora_hook_best_effort(prev_hooks, lora_name: str, strength_model: float, strength_clip: float):
    try:
        from comfy_extras import nodes_hooks
    except Exception:
        return prev_hooks

    try:
        creator = nodes_hooks.CreateHookLora()
    except Exception:
        return prev_hooks

    hook = None

    try:
        if hasattr(creator, "create_hook"):
            try:
                hook = creator.create_hook(prev_hooks, lora_name, strength_model, strength_clip)
            except Exception:
                try:
                    hook = creator.create_hook(lora_name, strength_model, strength_clip)
                except Exception:
                    hook = None
    except Exception:
        hook = None

    if hook is None:
        try:
            if hasattr(creator, "run"):
                try:
                    hook = creator.run(prev_hooks, lora_name, strength_model, strength_clip)
                except Exception:
                    try:
                        hook = creator.run(lora_name, strength_model, strength_clip)
                    except Exception:
                        hook = None
        except Exception:
            hook = None

    hook = _unwrap_single(hook)
    if prev_hooks is None:
        return hook
    return _combine_hooks_best_effort(prev_hooks, hook)


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
            },
            "optional": {
                "prev_hooks": ("HOOKS",),
            },
        }

    RETURN_TYPES = ("HOOKS", "STRING")
    RETURN_NAMES = ("hook", "trigger_text")
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

    def run(self, lora_name, trigger, strength_model, strength_clip, prev_hooks=None):
        hook = _create_lora_hook_best_effort(prev_hooks, lora_name, strength_model, strength_clip)
        text = self._read_trigger_text(lora_name, trigger)
        return (hook, text)


NODE_CLASS_MAPPINGS = {
    "LoraTriggerWithExample": LoraTriggerWithExample,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraTriggerWithExample": "LoRA Hook + Trigger Text",
}
