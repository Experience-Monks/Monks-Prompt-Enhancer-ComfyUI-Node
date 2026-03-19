import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MonksPromptEnhancer",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "MonksPromptEnhancer") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);
            this.color = "#1a3a5c";
            this.bgcolor = "#0f2235";
        };
    },
});
