import { app } from "/scripts/app.js";

function fetchTriggers(loraName) {
  const q = encodeURIComponent(loraName ?? "");
  return fetch(`/lora_trigger_list?lora_name=${q}`)
    .then((r) => r.json())
    .then((j) => Array.isArray(j?.triggers) && j.triggers.length ? j.triggers : ["NONE"])
    .catch(() => ["NONE"]);
}

app.registerExtension({
  name: "comfyui-lora-hook-trigger",

  async nodeCreated(node) {
    if (node?.comfyClass !== "LoraTriggerWithExample") return;

    const widgets = node.widgets || [];
    const loraWidget = widgets.find((w) => w?.name === "lora_name");
    const rawTrigger = widgets.find((w) => w?.name === "trigger");
    if (!loraWidget || !rawTrigger) return;

    rawTrigger.hidden = true;

    const uiTrigger = node.addWidget(
      "combo",
      "trigger",
      rawTrigger.value ?? "NONE",
      (v) => {
        rawTrigger.value = v ?? "NONE";
        node.setDirtyCanvas(true, true);
      },
      { values: ["NONE"] }
    );

    const reorderWidgets = () => {
      if (!node.widgets) return;
      const list = node.widgets;

      const rawIndex = list.indexOf(rawTrigger);
      if (rawIndex !== -1) list.splice(rawIndex, 1);
      list.push(rawTrigger);

      const uiIndex = list.indexOf(uiTrigger);
      const rawNewIndex = list.indexOf(rawTrigger);
      if (uiIndex !== -1 && rawNewIndex !== -1) {
        list.splice(uiIndex, 1);
        list.splice(rawNewIndex, 0, uiTrigger);
      }
    };

    const applyTriggerValues = (values) => {
      let v = Array.isArray(values) && values.length ? values : ["NONE"];
      if (!v.includes("NONE")) v = ["NONE", ...v];

      uiTrigger.options.values = v;

      const want = rawTrigger.value ?? uiTrigger.value ?? "NONE";
      if (v.includes(want)) {
        uiTrigger.value = want;
        rawTrigger.value = want;
      } else {
        uiTrigger.value = "NONE";
        rawTrigger.value = "NONE";
      }

      node.setDirtyCanvas(true, true);
    };

    const refresh = async () => {
      const loraName = loraWidget.value ?? "";
      const values = await fetchTriggers(loraName);
      applyTriggerValues(values);
      reorderWidgets();
    };

    const oldLoraCb = loraWidget.callback;
    loraWidget.callback = async (v) => {
      if (typeof oldLoraCb === "function") oldLoraCb(v);
      await refresh();
    };

    const oldConfigure = node.onConfigure;
    node.onConfigure = async function (info) {
      if (typeof oldConfigure === "function") oldConfigure.call(this, info);
      await refresh();
    };

    requestAnimationFrame(async () => {
      await refresh();
      setTimeout(refresh, 100);
    });
  },
});
