# ComfyUI LoRA Hook + Trigger Text Node

A clean and simple ComfyUI custom node that:

- Creates a LoRA Hook via `comfy_extras.nodes_hooks.CreateHookLora`
- Automatically finds and loads trigger TXT files placed in a folder named after the LoRA file
- Provides a trigger selection combo box in the UI
- Outputs both the generated hook and the selected trigger text

This node is designed to make using LoRA-specific trigger text easier and fully automated.

---

## 🔧 Features

- Automatic detection of `.txt` trigger files next to each LoRA
- UI dropdown for selecting trigger names
- Safe TXT reading with UTF-8 / UTF-8-SIG / CP949 fallback
- No external dependencies required
- Minimal and stable design

---

## 📁 Folder Structure

Examples (generic, not user data):

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

The folder name (my_lora) must match the LoRA file name without extension

Every .txt file inside that folder will appear in the trigger selector

If no TXT files are found, the trigger list defaults to NONE

📥 Installation
1) Install via ComfyUI Manager (Recommended)
Open ComfyUI Manager inside ComfyUI.

Go to Custom Nodes → Install via URL.

Paste this repository URL:
```text
https://github.com/akaugun/comfyui-lora-hook-trigger
```
Click Install.

Restart ComfyUI.

If the UI does not update after an extension update, hard refresh the browser:

Windows/Linux: Ctrl + F5

macOS: Cmd + Shift + R

2) Manual Installation
Place this repository into your ComfyUI custom_nodes folder:

ComfyUI/custom_nodes/comfyui-lora-hook-trigger
The folder structure must look like this:

comfyui-lora-hook-trigger/
├── __init__.py
└── js/
    └── lora_trigger_ui.js
Restart ComfyUI after installing.

🧩 Node Overview
Inputs
Name	Type	Description
lora_name	Combo	Select a LoRA installed under models/loras
trigger	String	Controlled by the UI; selected TXT file name (or NONE)
strength_model	Float	LoRA model strength
strength_clip	Float	LoRA CLIP strength

Outputs
Output	Type	Description
hook	HOOK	LoRA hook object that can be applied to models
example	String	Contents of the selected TXT file

🛠 How It Works (Simplified)
Python (__init__.py)
Defines the custom node class

Provides an HTTP endpoint: /lora_trigger_list

Locates the LoRA path using ComfyUI's folder_paths

Scans the corresponding folder for .txt files

Reads the selected TXT file

Builds the LoRA hook using CreateHookLora

JavaScript (js/lora_trigger_ui.js)
Adds a trigger dropdown to the node UI

Hides the raw trigger STRING field (still used for workflow serialization)

Syncs the dropdown value back into trigger

Calls /lora_trigger_list to refresh available triggers

⚙ Requirements
ComfyUI (latest recommended)

No additional dependencies

📄 License
See LICENSE.
