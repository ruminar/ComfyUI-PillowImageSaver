import ntpath
import os
import re
from datetime import datetime
from typing import Any, List, Optional, Tuple

import numpy as np
from PIL import Image

try:
    import folder_paths
except Exception:  # pragma: no cover - ComfyUI provides this module at runtime
    folder_paths = None

try:
    from comfy.utils import ProgressBar
except Exception:  # pragma: no cover - ComfyUI provides this module at runtime
    ProgressBar = None


TOOL_VERSION = "0.1.0"
TOOL_BUILD = "v2a"
BACKEND = "pillow"

DIRECTORY_PATTERNS = [
    "none",
    "date",
    "prefix",
    "prefix_date",
    "prefix/date",
    "label",
    "label_date",
    "label/date",
    "prefix_label",
    "prefix/label",
    "prefix_label_date",
    "prefix/label/date",
    "prefix_date_label",
    "prefix/date/label",
]

FILENAME_DATE_FORMATS = [
    "none",
    "yyyyMMdd",
    "yyyyMMdd_HHmm",
]

SUBSAMPLING_OPTIONS = ["4:4:4", "4:2:2", "4:2:0"]
SUBSAMPLING_TO_PILLOW = {
    "4:4:4": 0,
    "4:2:2": 1,
    "4:2:0": 2,
}

JPEG_EXTENSION = ".jpg"
INVALID_PATH_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
WHITESPACE_RE = re.compile(r"\s+")
MAX_PATH_PART_LENGTH = 120
MAX_FILENAME_STEM_LENGTH = 220
MAX_JPEG_COMMENT_BYTES = 65000

WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


class _NoopProgressBar:
    def update(self, amount: int = 1):
        return None


def _make_progress_bar(total: int):
    if ProgressBar is None:
        return _NoopProgressBar()
    try:
        return ProgressBar(total)
    except Exception:
        return _NoopProgressBar()


def _get_comfy_output_directory() -> str:
    if folder_paths is None:
        raise RuntimeError("ComfyUI folder_paths module is not available.")
    return folder_paths.get_output_directory()


def _sanitize_path_part(value: Any, fallback: str = "unnamed") -> str:
    text = str(value if value is not None else "").strip()
    text = INVALID_PATH_CHARS_RE.sub("_", text)
    text = WHITESPACE_RE.sub("_", text)
    text = text.strip("._ ")
    if not text:
        text = fallback

    if text.upper() in WINDOWS_RESERVED_NAMES:
        text = f"{text}_"

    if len(text) > MAX_PATH_PART_LENGTH:
        text = text[:MAX_PATH_PART_LENGTH].rstrip("._ ") or fallback
    return text


def _limit_filename_stem(stem: str) -> str:
    stem = stem.strip("._ ") or "image"
    if len(stem) > MAX_FILENAME_STEM_LENGTH:
        stem = stem[:MAX_FILENAME_STEM_LENGTH].rstrip("._ ") or "image"
    return stem


def _build_file_date_text(filename_date_format: str, now: datetime) -> str:
    if filename_date_format == "none":
        return ""
    if filename_date_format == "yyyyMMdd":
        return now.strftime("%Y%m%d")
    if filename_date_format == "yyyyMMdd_HHmm":
        return now.strftime("%Y%m%d_%H%M")
    raise ValueError(f"Unsupported filename_date_format: {filename_date_format}")


def _build_dir_date_text(now: datetime) -> str:
    return now.strftime("%Y%m%d")


def _relative_path_has_parent_reference(path_text: str) -> bool:
    parts = path_text.replace("\\", "/").split("/")
    return any(part == ".." for part in parts)


def _is_windows_drive_relative_path(path_text: str) -> bool:
    drive, _tail = ntpath.splitdrive(path_text)
    return bool(drive) and not ntpath.isabs(path_text)


def _resolve_base_output_dir(output_dir: Optional[str]) -> str:
    if output_dir is None:
        return _get_comfy_output_directory()

    raw = str(output_dir).strip()
    if not raw:
        return _get_comfy_output_directory()

    if _is_windows_drive_relative_path(raw):
        raise RuntimeError(
            "Drive-relative output_dir paths such as 'C:foo' are not supported. "
            "Use an absolute path such as 'C:\\foo'."
        )

    if os.path.isabs(raw):
        return os.path.normpath(raw)

    if _relative_path_has_parent_reference(raw):
        raise RuntimeError(
            "Relative output_dir must not contain '..'. "
            "Use an absolute path if you want to save outside the ComfyUI output directory."
        )

    return os.path.normpath(os.path.join(_get_comfy_output_directory(), raw))


def _requires_label(directory_pattern: str) -> bool:
    return "label" in directory_pattern


def _build_directory_parts(
    directory_pattern: str,
    prefix_safe: str,
    label_safe: Optional[str],
    dir_date_text: str,
) -> List[str]:
    if directory_pattern not in DIRECTORY_PATTERNS:
        raise ValueError(f"Unsupported directory_pattern: {directory_pattern}")

    if _requires_label(directory_pattern) and not label_safe:
        raise RuntimeError(
            "directory_pattern uses label, but no label string was provided. "
            "Connect a STRING node to the label input, or choose a pattern without label."
        )

    if directory_pattern == "none":
        return []
    if directory_pattern == "date":
        return [dir_date_text]
    if directory_pattern == "prefix":
        return [prefix_safe]
    if directory_pattern == "prefix_date":
        return [f"{prefix_safe}_{dir_date_text}"]
    if directory_pattern == "prefix/date":
        return [prefix_safe, dir_date_text]
    if directory_pattern == "label":
        return [label_safe]
    if directory_pattern == "label_date":
        return [f"{label_safe}_{dir_date_text}"]
    if directory_pattern == "label/date":
        return [label_safe, dir_date_text]
    if directory_pattern == "prefix_label":
        return [f"{prefix_safe}_{label_safe}"]
    if directory_pattern == "prefix/label":
        return [prefix_safe, label_safe]
    if directory_pattern == "prefix_label_date":
        return [f"{prefix_safe}_{label_safe}_{dir_date_text}"]
    if directory_pattern == "prefix/label/date":
        return [prefix_safe, label_safe, dir_date_text]
    if directory_pattern == "prefix_date_label":
        return [f"{prefix_safe}_{dir_date_text}_{label_safe}"]
    if directory_pattern == "prefix/date/label":
        return [prefix_safe, dir_date_text, label_safe]

    raise ValueError(f"Unsupported directory_pattern: {directory_pattern}")


def _build_save_dir(
    output_dir: Optional[str],
    directory_pattern: str,
    prefix_safe: str,
    label_safe: Optional[str],
    dir_date_text: str,
) -> str:
    base_dir = _resolve_base_output_dir(output_dir)
    parts = _build_directory_parts(directory_pattern, prefix_safe, label_safe, dir_date_text)
    save_dir = os.path.join(base_dir, *parts) if parts else base_dir
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def _build_filename_stem(
    prefix_safe: str,
    label_safe: Optional[str],
    file_date_text: str,
) -> str:
    parts = [prefix_safe]
    if label_safe:
        parts.append(label_safe)
    if file_date_text:
        parts.append(file_date_text)
    return _limit_filename_stem("_".join(parts))


def _next_counter(save_dir: str, stem: str) -> int:
    prefix = f"{stem}_"
    prefix_casefold = prefix.casefold()
    max_counter = 0
    try:
        names = os.listdir(save_dir)
    except FileNotFoundError:
        return 1

    for name in names:
        name_casefold = name.casefold()
        if not name_casefold.endswith(JPEG_EXTENSION):
            continue
        if not name_casefold.startswith(prefix_casefold):
            continue
        tail = name_casefold[len(prefix_casefold):-len(JPEG_EXTENSION)]
        if tail.isdigit():
            max_counter = max(max_counter, int(tail))
    return max_counter + 1


def _tensor_to_rgb_array_and_size(image_tensor) -> Tuple[np.ndarray, int, int]:
    img = image_tensor.cpu().numpy()
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)

    if img.ndim != 3:
        raise RuntimeError(f"Expected image tensor with 3 dimensions (HWC), got shape {img.shape}")

    h, w, c = img.shape
    if c == 1:
        img = np.repeat(img, 3, axis=2)
    elif c == 4:
        img = img[:, :, :3]
    elif c != 3:
        raise RuntimeError(f"Expected 1, 3, or 4 channels, got shape {img.shape}")

    return np.ascontiguousarray(img), int(w), int(h)


def _normalize_comment(comment: Optional[str]) -> Optional[bytes]:
    if comment is None:
        return None
    text = str(comment)
    if not text:
        return None
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_JPEG_COMMENT_BYTES:
        encoded = (
            encoded[:MAX_JPEG_COMMENT_BYTES]
            .decode("utf-8", errors="ignore")
            .encode("utf-8")
        )
    return encoded


def _save_jpeg_exclusive(
    pil_image: Image.Image,
    save_dir: str,
    stem: str,
    counter: int,
    save_kwargs: dict,
) -> int:
    while True:
        filename = f"{stem}_{counter:04}.jpg"
        out_path = os.path.join(save_dir, filename)

        try:
            file_handle = open(out_path, "xb")
        except FileExistsError:
            counter += 1
            continue

        try:
            with file_handle:
                pil_image.save(file_handle, **save_kwargs)
        except BaseException:
            try:
                os.remove(out_path)
            except OSError:
                pass
            raise

        return counter


class PillowImageJpegSave:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "image"}),
                "directory_pattern": (DIRECTORY_PATTERNS, {"default": "prefix/date"}),
                "filename_date_format": (FILENAME_DATE_FORMATS, {"default": "none"}),
                "quality": ("INT", {"default": 80, "min": 1, "max": 100, "step": 1}),
                "subsampling": (SUBSAMPLING_OPTIONS, {"default": "4:2:2"}),
                "progressive": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "output_dir": ("STRING", {"forceInput": True}),
                "label": ("STRING", {"forceInput": True}),
                "comment": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image/PillowImageSaver"

    def save_images(
        self,
        images,
        filename_prefix,
        directory_pattern,
        filename_date_format,
        quality,
        subsampling,
        progressive,
        output_dir=None,
        label=None,
        comment=None,
    ):
        now = datetime.now()
        prefix_safe = _sanitize_path_part(filename_prefix, fallback="image")
        label_safe = None
        if label is not None and str(label).strip():
            label_safe = _sanitize_path_part(label, fallback="label")

        dir_date_text = _build_dir_date_text(now)
        file_date_text = _build_file_date_text(filename_date_format, now)
        save_dir = _build_save_dir(output_dir, directory_pattern, prefix_safe, label_safe, dir_date_text)
        stem = _build_filename_stem(prefix_safe, label_safe, file_date_text)
        counter = _next_counter(save_dir, stem)

        pillow_subsampling = SUBSAMPLING_TO_PILLOW[subsampling]
        comment_bytes = _normalize_comment(comment)
        pbar = _make_progress_bar(len(images))

        for image in images:
            rgb_array, _w, _h = _tensor_to_rgb_array_and_size(image)
            pil_image = Image.fromarray(rgb_array)

            save_kwargs = {
                "format": "JPEG",
                "quality": int(quality),
                "subsampling": pillow_subsampling,
                "progressive": bool(progressive),
            }
            if comment_bytes:
                save_kwargs["comment"] = comment_bytes

            try:
                counter = _save_jpeg_exclusive(
                    pil_image,
                    save_dir,
                    stem,
                    counter,
                    save_kwargs,
                )
            except OSError as exc:
                raise RuntimeError(
                    f"Pillow failed while saving a JPEG in '{save_dir}'."
                ) from exc

            counter += 1
            pbar.update(1)

        return {}
