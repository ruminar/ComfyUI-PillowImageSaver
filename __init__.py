from .nodes import PillowImageJpegSave

NODE_CLASS_MAPPINGS = {
    "PillowImageJpegSave": PillowImageJpegSave,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PillowImageJpegSave": "Pillow Image JPEG Save",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
