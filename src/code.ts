// Figma Plugin: Copy to Chronicle
// Main plugin thread — has access to the Figma document API.
// Communicates with the UI via postMessage.

figma.showUI(__html__, { width: 320, height: 300, title: "Copy to Chronicle" });

// ── Types ──────────────────────────────────────────────────────────────────

type SelectionMsg = {
  type: "SELECTION";
  hasSelection: boolean;
  name: string;
  nodeType: string;
};

type ExportResultMsg = {
  type: "EXPORT_RESULT";
  format: "PNG" | "SVG";
  data: string; // Base64 for PNG, raw string for SVG
};

type ErrorMsg = {
  type: "ERROR";
  message: string;
};

type ExportRequest = {
  type: "EXPORT";
  format: "PNG" | "SVG";
  scale: number;
};

type CloseRequest = { type: "CLOSE" };

type UIMessage = ExportRequest | CloseRequest;

// ── Helpers ────────────────────────────────────────────────────────────────

// Pure JS base64 — btoa() is a browser API not available in Figma's QuickJS sandbox.
function uint8ToBase64(bytes: Uint8Array): string {
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

function getSelection(): SceneNode | null {
  const sel = figma.currentPage.selection;
  return sel.length > 0 ? sel[0] : null;
}

function sendSelection(): void {
  const node = getSelection();
  const msg: SelectionMsg = node
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

figma.ui.onmessage = async (msg: UIMessage) => {
  if (msg.type === "CLOSE") {
    figma.closePlugin();
    return;
  }

  if (msg.type === "EXPORT") {
    const node = getSelection();
    if (!node) {
      const err: ErrorMsg = { type: "ERROR", message: "No element selected." };
      figma.ui.postMessage(err);
      return;
    }

    try {
      if (msg.format === "SVG") {
        const svgString = await node.exportAsync({ format: "SVG_STRING" });
        const result: ExportResultMsg = { type: "EXPORT_RESULT", format: "SVG", data: svgString };
        figma.ui.postMessage(result);
      } else {
        const scale = msg.scale ?? 2;
        const pngBytes = await node.exportAsync({
          format: "PNG",
          constraint: { type: "SCALE", value: scale },
        });
        const result: ExportResultMsg = {
          type: "EXPORT_RESULT",
          format: "PNG",
          data: uint8ToBase64(pngBytes),
        };
        figma.ui.postMessage(result);
      }
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Export failed.";
      const err: ErrorMsg = { type: "ERROR", message };
      figma.ui.postMessage(err);
    }
  }
};
