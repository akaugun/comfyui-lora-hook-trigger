import { app } from "/scripts/app.js";

app.registerExtension({
    name: "lora_trigger_example",

    async nodeCreated(node) {
        if (node.comfyClass !== "LoraTriggerWithExample") return;

        const widgets = node.widgets || [];
        const rawTrigger = widgets.find((w) => w.name === "trigger");
        const loraWidget = widgets.find((w) => w.name === "lora_name");

        if (!rawTrigger || !loraWidget) return;

        rawTrigger.hidden = true;

        const uiTrigger = node.addWidget(
            "combo",
            "trigger",
            "NONE",
            (value) => {
                rawTrigger.value = value;
            },
            { values: ["NONE"] }
        );

        if (node.widgets && node.widgets.length > 0) {
            const list = node.widgets;
            const uiIndex = list.indexOf(uiTrigger);
            const rawIndex = list.indexOf(rawTrigger);

            if (uiIndex !== -1 && rawIndex !== -1) {
                list.splice(uiIndex, 1);
                list.splice(rawIndex, 0, uiTrigger);

                const newRawIndex = list.indexOf(rawTrigger);
                if (newRawIndex !== -1) {
                    list.splice(newRawIndex, 1);
                    list.push(rawTrigger);
                }
            }
        }

        async function updateTriggers() {
            const lora = loraWidget.value;
            let values = ["NONE"];

            if (!lora) {
                uiTrigger.options.values = values;
                uiTrigger.value = "NONE";
                rawTrigger.value = "NONE";
                if (typeof node.onResize === "function") node.onResize();
                return;
            }

            try {
                const resp = await fetch(
                    "/lora_trigger_list?lora_name=" +
                        encodeURIComponent(lora),
                    { method: "GET" }
                );

                if (resp.ok) {
                    const data = await resp.json();
                    if (
                        data &&
                        Array.isArray(data.triggers) &&
                        data.triggers.length > 0
                    ) {
                        values = data.triggers;
                    }
                }
            } catch (e) {}

            if (!values.includes("NONE")) {
                values = ["NONE", ...values.filter((v) => v !== "NONE")];
            }

            uiTrigger.options.values = values;

            if (!values.includes(uiTrigger.value)) {
                uiTrigger.value = values[0];
            }

            rawTrigger.value = uiTrigger.value;

            if (typeof node.onResize === "function") node.onResize();
        }

        const origCallback = loraWidget.callback;
        loraWidget.callback = function () {
            if (origCallback) origCallback.apply(this, arguments);
            updateTriggers();
        };

        setTimeout(updateTriggers, 50);
    },
});
