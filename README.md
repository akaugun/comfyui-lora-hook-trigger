# ComfyUI LoRA Hook + Trigger Text Node

A clean and simple ComfyUI custom node that:

- Creates a LoRA Hook through `comfy_extras.nodes_hooks.CreateHookLora`
- Automatically finds and loads trigger TXT files placed in a folder named after the LoRA file
- Provides a trigger selection combo box in the UI
- Outputs both the generated Hook and the selected trigger text

This node makes using LoRA-specific trigger text easier and fully automated.

---

## 🔧 Features

- Automatic detection of TXT trigger files next to each LoRA
- Clean UI combo box for selecting trigger names
- Safe TXT reading with UTF-8 / UTF-8-SIG / CP949 fallback
- No external dependencies
- Works on all standard ComfyUI installations

---

## 📁 Folder Structure Example

These are **generic examples**, not user data.

models/loras/my_lora.safetensors
models/loras/my_lora/trigger1.txt
models/loras/my_lora/style.txt
models/loras/my_lora/preset_prompt.txt

markdown
코드 복사

Rules:

- The folder name (`my_lora`) must match the LoRA file name **without extension**
- Every `.txt` file inside that folder appears in the trigger selector
- If no TXT files are found, the trigger list defaults to:

["NONE"]

yaml
코드 복사

---

## 📥 Installation

Place this repository inside your ComfyUI `custom_nodes` folder:

ComfyUI/custom_nodes/comfyui-lora-hook-trigger

vbnet
코드 복사

Folder structure should look like:

comfyui-lora-hook-trigger/
├── init.py
└── js/
└── lora_trigger_ui.js

yaml
코드 복사

Restart ComfyUI after installing.

---

## 🧩 Node Overview

### **Inputs**

| Name            | Type   | Description |
|-----------------|--------|-------------|
| `lora_name`     | Combo  | Select a LoRA from `models/loras` |
| `trigger`       | String | Auto-filled by UI |
| `strength_model` | Float | LoRA strength for model |
| `strength_clip`  | Float | LoRA strength for CLIP |

### **Outputs**

| Output    | Type  | Description |
|-----------|-------|-------------|
| `HOOKS`   | Hook  | LoRA hook object |
| `example` | String| Contents of selected TXT |

---

## 🛠 How It Works (Simplified)

### **Python (`__init__.py`):**

- Defines the custom node
- Provides HTTP endpoint: `/lora_trigger_list`
- Locates LoRA path via `folder_paths`
- Scans folder for TXT files
- Reads selected TXT file
- Creates LoRA Hook via `CreateHookLora`

### **JavaScript (`js/lora_trigger_ui.js`):**

- Adds trigger dropdown to UI
- Hides raw STRING widget
- Keeps UI value synced to backend
- Calls server endpoint to refresh trigger list

---

## ⚙ Requirements

- ComfyUI (latest recommended)
- No additional dependencies

---

## 📄 License

You may choose any license later.  
For now, this project is shared for community use.
