# ImageSaver family shared specification

Projects:

- ComfyUI-GMImageSaver
- ComfyUI-PillowImageSaver

## Shared node behavior

Both sibling projects should keep the same user-facing behavior where possible.

- JPEG-only output node
- No preview output
- No `IMAGE` passthrough
- `RETURN_TYPES = ()`
- `OUTPUT_NODE = True`
- Return `{}`
- Optional `output_dir`, `label`, and `comment` input pins
- `label` may receive `ckpt_name_safe` from HandpickerSuite, but no direct dependency is allowed
- Existing `ckpt_name_safe` hyphens must be preserved
- Date text is captured once per node execution
- Counter is fixed four digits
- Progress bar updates once per successfully saved image

## Default widget values

```text
filename_prefix: image
directory_pattern: prefix/date
filename_date_format: none
quality: 80
subsampling: 4:2:2
progressive: false
```

## Directory patterns

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

## Filename date formats

```text
none
yyyyMMdd
yyyyMMdd_HHmm
```
