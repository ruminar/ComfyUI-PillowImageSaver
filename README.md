# ComfyUI-PillowImageSaver

Pillow-based image saver nodes for ComfyUI.

The initial node, **Pillow Image JPEG Save**, is an output-only JPEG saver. It saves ComfyUI `IMAGE` tensors directly as JPEG files using Pillow, without returning preview images.

This project is a Pillow-based sibling of [ComfyUI-GMImageSaver](https://github.com/ruminar/ComfyUI-GMImageSaver). The user-facing workflow is intentionally kept close to GMImageSaver, while replacing the GraphicsMagick backend with Pillow.

## Node

### Pillow Image JPEG Save

A deliberately narrow JPEG saver node.

It does **not** try to be a general image saver.

- JPEG only
- No PNG output
- No preview output
- No `IMAGE` passthrough
- No external command execution
- No HandpickerSuite dependency
- Optional JPEG comment via input pin only
- Optional `label` input pin for filename and directory naming
- Image-by-image progress bar updates

For PNG output, use ComfyUI's standard Save Image node.

## Requirements

Pillow is required.

Most ComfyUI environments already include Pillow, but this repository also provides `requirements.txt` so dependency installation can be handled by ComfyUI Manager or your usual Python environment.

## Inputs

Required:

- `images`: ComfyUI `IMAGE`
- `filename_prefix`: filename prefix. Default: `image`
- `directory_pattern`: directory layout pattern. Default: `prefix/date`
- `filename_date_format`: optional date text in the filename. Default: `none`
- `quality`: JPEG quality, from `1` to `100`. Default: `80`
- `subsampling`: JPEG chroma subsampling. Default: `4:2:2`
- `progressive`: progressive JPEG. Default: `False`

Optional input pins:

- `output_dir`: base output directory. Connect from a string/text node.
- `label`: optional extra naming string. You can connect `ckpt_name_safe` or any other label string.
- `comment`: JPEG comment string. Connect from a string/text node.

If `output_dir` is unconnected or empty, ComfyUI's standard output directory is used.

If `output_dir` is a relative path, it is resolved under ComfyUI's standard output directory.

If `output_dir` is an absolute path, it is used as-is.

Windows drive-relative paths such as `C:foo` are rejected. Use an absolute path such as `C:\foo` instead.

## Directory patterns

`directory_pattern` controls folders under `output_dir`.

The `date` part is always `yyyyMMdd`.

Available patterns:

```text
none
date
prefix
prefix_date
prefix/date
label
label_date
label/date
prefix_label
prefix/label
prefix_label_date
prefix/label/date
prefix_date_label
prefix/date/label
```

Example values:

```text
output_dir: D:\ComfyJPEG
filename_prefix: image
label: meinamix_v11
date: 20260601
```

Results:

```text
none                -> D:\ComfyJPEG
date                -> D:\ComfyJPEG\20260601
prefix              -> D:\ComfyJPEG\image
prefix_date         -> D:\ComfyJPEG\image_20260601
prefix/date         -> D:\ComfyJPEG\image\20260601
label               -> D:\ComfyJPEG\meinamix_v11
label_date          -> D:\ComfyJPEG\meinamix_v11_20260601
label/date          -> D:\ComfyJPEG\meinamix_v11\20260601
prefix_label        -> D:\ComfyJPEG\image_meinamix_v11
prefix/label        -> D:\ComfyJPEG\image\meinamix_v11
prefix_label_date   -> D:\ComfyJPEG\image_meinamix_v11_20260601
prefix/label/date   -> D:\ComfyJPEG\image\meinamix_v11\20260601
prefix_date_label   -> D:\ComfyJPEG\image_20260601_meinamix_v11
prefix/date/label   -> D:\ComfyJPEG\image\20260601\meinamix_v11
```

Patterns containing `label` require a `label` input.

## Filename date formats

`filename_date_format` controls date text in the filename, not the directory.

Available values:

```text
none
yyyyMMdd
yyyyMMdd_HHmm
```

The counter is four digits.

Examples:

```text
image_0001.jpg
image_20260601_0001.jpg
image_20260601_1423_0001.jpg
image_meinamix_v11_0001.jpg
image_meinamix_v11_20260601_1423_0001.jpg
```

If `label` is connected, it is included in the filename automatically.

The timestamp is fixed once per node execution, so images in the same batch use the same timestamp.

## Suggested workflow

For large batch or checkpoint inventory workflows, the default settings are intentionally moderate:

```text
quality: 80
subsampling: 4:2:2
```

After selecting favorite checkpoints or images, you can raise the settings, for example:

```text
quality: 95
subsampling: 4:4:4
```

This keeps initial inventory output lighter while still allowing higher-quality final output.

## HandpickerSuite workflow

This node does not depend on HandpickerSuite.

However, it works well with checkpoint inventory workflows such as [ComfyUI-CheckpointHandpickerSuite](https://github.com/ruminar/ComfyUI-CheckpointHandpickerSuite).

For example:

```text
ckpt_name_safe -> label
```

This allows generated images to be saved with checkpoint-aware filenames and directory structures while keeping both projects loosely coupled.

## Progress

The node updates ComfyUI's progress bar once per successfully saved image.

## Preview policy

This node intentionally does not return preview images.

For previews, branch the `IMAGE` before this node and connect it to your preferred preview node.

Example:

```text
VAE Decode / IMAGE
  ├─ Preview node
  └─ Pillow Image JPEG Save
```

## License

GPL-3.0
