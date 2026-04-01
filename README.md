# Figma → Chronicle Plugin

A Figma plugin to copy any selected element — shapes, vectors, images, frames, components — and paste it directly into [Chronicle HQ](https://app.chroniclehq.com) slides.

> **Note:** The clipboard approach is a temporary solution while Chronicle's API is in development. The `sendToChronicle()` function in `src/ui.html` is already stubbed for a direct API integration once it's available.

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

- [Node.js](https://nodejs.org/) (v18 or later)
- [Git](https://git-scm.com/)
- [Figma Desktop](https://www.figma.com/downloads/) (plugins only run in the desktop app, not the browser)

---

### 1. Clone the repo

```bash
git clone https://github.com/oyeabhijit/figma-to-chronicle.git
cd figma-to-chronicle
```

---

### 2. Install dependencies

```bash
npm install
```

---

### 3. Build the plugin

```bash
npm run build
```

This compiles `src/code.ts` → `dist/code.js`. Run `npm run watch` to auto-rebuild on changes during development.

---

### 4. Load the plugin in Figma Desktop

1. Open **Figma Desktop**
2. Go to **Menu → Plugins → Development → Import plugin from manifest...**
3. Navigate to the cloned folder and select **`manifest.json`**
4. The plugin will now appear under **Plugins → Development → Copy to Chronicle**

---

### 5. Test the plugin

1. Open any Figma file and select an element (shape, image, frame, etc.)
2. Run **Plugins → Development → Copy to Chronicle**
3. Choose **SVG** or **PNG** (with scale), then click **Copy to Clipboard**
4. Paste into a [Chronicle](https://app.chroniclehq.com) slide

---

## Project Structure

```
figma-to-chronicle/
├── manifest.json          # Figma plugin config (entry points, permissions)
├── package.json           # Dev dependencies and build scripts
├── tsconfig.json          # TypeScript config
├── src/
│   ├── code.ts            # Main plugin thread — Figma API, export, base64
│   └── ui.html            # Plugin UI — format picker, clipboard logic
└── dist/
    └── code.js            # Compiled output (auto-generated, do not edit)
```

---

## Contributing

### 1. Create a branch

Always work on a new branch — never commit directly to `main`.

```bash
git checkout -b your-name/short-description
# e.g. git checkout -b alex/fix-png-clipboard
```

### 2. Make your changes

Edit files in `src/`. Run `npm run watch` so the build updates automatically:

```bash
npm run watch
```

Reload the plugin in Figma after each build:
- Go to **Plugins → Development → Copy to Chronicle**
- Hold **Option (Mac)** and click the plugin name to get a **Reload** option, or just re-run it

### 3. Commit your changes

```bash
git add src/manifest.json   # stage only the files you changed
git commit -m "fix: describe what you changed and why"
```

Follow this commit format:
| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `refactor:` | Code cleanup, no behaviour change |
| `docs:` | README or comments only |
| `chore:` | Build, config, dependencies |

### 4. Push your branch

```bash
git push origin your-name/short-description
```

### 5. Open a Pull Request

1. Go to [github.com/oyeabhijit/figma-to-chronicle](https://github.com/oyeabhijit/figma-to-chronicle)
2. Click **"Compare & pull request"** (appears automatically after push)
3. Fill in:
   - **Title** — short summary of the change
   - **Description** — what you changed, why, and how to test it
4. Request a review and click **Create pull request**

---

## Known Issue — Clipboard (active bug)

Copying as a real image (`image/png`) to the clipboard is currently blocked by Figma's sandboxed iframe environment (`sandbox="allow-scripts"`, null origin). All three approaches tried so far fail:

| Method | Result |
|--------|--------|
| `navigator.clipboard.write` + `ClipboardItem` | Blocked — null origin can't get `clipboard-write` permission |
| `execCommand('copy')` + `text/html` | Clipboard gets HTML but Figma/Chronicle strip `data:` URLs → blank paste |
| `contenteditable` + select + `execCommand` | Same stripping issue in Figma's Electron sandbox |

See [`figma-chronicle-debug.pdf`](./generate_debug_doc.py) for the full technical breakdown (run `python3 generate_debug_doc.py` to regenerate it).

**If you're investigating a fix**, the entire clipboard logic lives in `writeToClipboard()` in `src/ui.html`. Everything else in the plugin works correctly.

---

## Future: Chronicle API Integration

When Chronicle's API is available, replace the `writeToClipboard()` call inside `sendToChronicle()` in `src/ui.html` with a `fetch()` POST:

```js
async function sendToChronicle(data, format) {
  // Replace this:
  await writeToClipboard(dataUrl);

  // With this:
  await fetch('https://app.chroniclehq.com/api/v1/slides/current/assets', {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}` },
    body: JSON.stringify({ format, data }),
  });
}
```

You'll also need to add `app.chroniclehq.com` to `networkAccess.allowedDomains` in `manifest.json`.
