"use strict";
// Figma Plugin: Copy to Chronicle
// Main plugin thread — has access to the Figma document API.
// Communicates with the UI via postMessage.
figma.showUI(__html__, { width: 320, height: 300, title: "Copy to Chronicle" });
// ── Helpers ────────────────────────────────────────────────────────────────
// Pure JS base64 — btoa() is a browser API not available in Figma's QuickJS sandbox.
function uint8ToBase64(bytes) {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let result = "";
    const len = bytes.length;
    for (let i = 0; i < len; i += 3) {
        const b0 = bytes[i];
        const b1 = i + 1 < len ? bytes[i + 1] : 0;
        const b2 = i + 2 < len ? bytes[i + 2] : 0;
        result += chars[b0 >> 2];
        result += chars[((b0 & 3) << 4) | (b1 >> 4)];
        result += i + 1 < len ? chars[((b1 & 15) << 2) | (b2 >> 6)] : "=";
        result += i + 2 < len ? chars[b2 & 63] : "=";
    }
    return result;
}
function getSelection() {
    const sel = figma.currentPage.selection;
    return sel.length > 0 ? sel[0] : null;
}
function sendSelection() {
    const node = getSelection();
    const msg = node
        ? { type: "SELECTION", hasSelection: true, name: node.name, nodeType: node.type }
        : { type: "SELECTION", hasSelection: false, name: "", nodeType: "" };
    figma.ui.postMessage(msg);
}
// ── Init: send current selection state ────────────────────────────────────
sendSelection();
// ── Selection change listener ──────────────────────────────────────────────
figma.on("selectionchange", () => {
    sendSelection();
});
// ── Message handler ────────────────────────────────────────────────────────
figma.ui.onmessage = async (msg) => {
    var _a;
    if (msg.type === "CLOSE") {
        figma.closePlugin();
        return;
    }
    if (msg.type === "EXPORT") {
        const node = getSelection();
        if (!node) {
            const err = { type: "ERROR", message: "No element selected." };
            figma.ui.postMessage(err);
            return;
        }
        try {
            if (msg.format === "SVG") {
                const svgString = await node.exportAsync({ format: "SVG_STRING" });
                const result = { type: "EXPORT_RESULT", format: "SVG", data: svgString };
                figma.ui.postMessage(result);
            }
            else {
                const scale = (_a = msg.scale) !== null && _a !== void 0 ? _a : 2;
                const pngBytes = await node.exportAsync({
                    format: "PNG",
                    constraint: { type: "SCALE", value: scale },
                });
                const result = {
                    type: "EXPORT_RESULT",
                    format: "PNG",
                    data: uint8ToBase64(pngBytes),
                };
                figma.ui.postMessage(result);
            }
        }
        catch (e) {
            const message = e instanceof Error ? e.message : "Export failed.";
            const err = { type: "ERROR", message };
            figma.ui.postMessage(err);
        }
    }
};
