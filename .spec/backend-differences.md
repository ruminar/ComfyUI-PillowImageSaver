# Backend differences

## GMImageSaver

- Backend: GraphicsMagick CLI
- Node display name: `GM Image JPEG Save`
- External GraphicsMagick installation required
- Uses raw RGB pipe to `gm convert`
- May require manual Comfy Registry security review because it invokes an external command

## PillowImageSaver

- Backend: Pillow
- Node display name: `Pillow Image JPEG Save`
- Python dependency: Pillow
- No external command execution
- Uses `PIL.Image.save(..., format="JPEG")`
- Should keep the same naming, directory, label, comment, and progress behavior as GMImageSaver where possible
