// Figma Plugin: Copy to Chronicle
// Main plugin thread — compiled from src/code.ts

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

// ── Init ───────────────────────────────────────────────────────────────────

sendSelection();

figma.on("selectionchange", () => {
  sendSelection();
});

// ── Message handler ────────────────────────────────────────────────────────

figma.ui.onmessage = async (msg) => {
  if (msg.type === "CLOSE") {
    figma.closePlugin();
    return;
  }

  if (msg.type === "EXPORT") {
    const node = getSelection();
    if (!node) {
      figma.ui.postMessage({ type: "ERROR", message: "No element selected." });
      return;
    }

    try {
      if (msg.format === "SVG") {
        const svgString = await node.exportAsync({ format: "SVG_STRING" });
        figma.ui.postMessage({ type: "EXPORT_RESULT", format: "SVG", data: svgString });
      } else {
        const scale = msg.scale != null ? msg.scale : 2;
        const pngBytes = await node.exportAsync({
          format: "PNG",
          constraint: { type: "SCALE", value: scale },
        });
        figma.ui.postMessage({
          type: "EXPORT_RESULT",
          format: "PNG",
          data: uint8ToBase64(pngBytes),
        });
      }
    } catch (e) {
      const message = e instanceof Error ? e.message : "Export failed.";
      figma.ui.postMessage({ type: "ERROR", message });
    }
  }
};
