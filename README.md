# ComfyUI LoRA Hook + Trigger Text Node

A clean and simple ComfyUI custom node that:

- Creates a LoRA Hook through `comfy_extras.nodes_hooks.CreateHookLora`
- Automatically finds and loads trigger TXT files placed in a folder named after the LoRA file
- Provides a trigger selection combo box in the UI
- Outputs both the generated Hook and the selected trigger text

This node is designed to make using LoRA-specific trigger text easier and fully automated.

---

## 🔧 Features

- Automatic detection of TXT trigger files next to each LoRA
- Clean UI combo box for selecting trigger names
- Safe TXT reading with UTF-8 / UTF-8-SIG / CP949 fallback
- No external dependencies required
- Minimal, stable design that works across any ComfyUI installation

---

## 📁 Folder Structure Example

These are generic examples, not user data.

```text
models/
└── loras/
    ├── my_lora.safetensors
    └── my_lora/
        ├── trigger1.txt
        ├── style.txt
        └── preset_prompt.txt
```

Rules:

- The folder name (`my_lora`) must match the LoRA file name **without extension**
- Every `.txt` file inside that folder will appear in the trigger selector
- If no TXT files are found, the trigger list defaults to:

["NONE"]


---

## 📥 Installation

### 1) Install via ComfyUI Manager (Recommended)

1. Open **ComfyUI Manager** inside ComfyUI.
2. Go to **Custom Nodes → Install via URL**.
3. Paste this repository URL: https://github.com/akaugun/comfyui-lora-hook-trigger
4. Click **Install**.
5. Restart ComfyUI.

---

### 2) Manual Installation

Place this repository into your ComfyUI `custom_nodes` folder:

ComfyUI/custom_nodes/comfyui-lora-hook-trigger
The folder structure must look like this:
```text
comfyui-lora-hook-trigger/
├── __init__.py
└── js/
    └── lora_trigger_ui.js
```
Restart ComfyUI after installing.

---

## 🧩 Node Overview

### Inputs

| Name            | Type   | Description |
|-----------------|--------|-------------|
| `lora_name`     | Combo  | Select a LoRA installed under `models/loras` |
| `trigger`       | String | Controlled by UI; represents selected TXT file name |
| `strength_model` | Float | LoRA model strength |
| `strength_clip`  | Float | LoRA CLIP strength |

### Outputs

| Output    | Type  | Description |
|-----------|-------|-------------|
| `HOOKS`   | Hook  | LoRA hook object that can be applied to models |
| `example` | String| Contents of the selected TXT file |

---

## 🛠 How It Works (Simplified)

### Python (`__init__.py`)

- Defines the custom node class  
- Provides an HTTP endpoint `/lora_trigger_list`  
- Locates the LoRA path using ComfyUI's `folder_paths`  
- Scans the corresponding folder for TXT files  
- Reads the selected TXT file  
- Builds the LoRA Hook with `CreateHookLora`  

### JavaScript (`js/lora_trigger_ui.js`)

- Inserts a trigger dropdown into the node UI  
- Hides the raw `trigger` STRING field  
- Syncs the UI value back into the node  
- Calls the server endpoint to update available triggers  

---

## ⚙ Requirements

- ComfyUI (latest recommended)
- No additional dependencies
- Works on all operating systems supported by ComfyUI

---

## 📄 License

You may choose any license you prefer later.  
For now, this project is shared as-is for community usage.
