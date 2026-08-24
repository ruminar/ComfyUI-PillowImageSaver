# Release Notes

## 0.1.1 - Safer JPEG output

This maintenance release improves filename collision handling, output path safety, and JPEG comment integrity.

### Fixed

* Continues filename numbering correctly beyond four digits, preventing an existing `image_10000.jpg` from being overwritten after the counter passes `9999`.
* Matches existing filename stems case-insensitively, preventing case-only names such as `Cat_0001.jpg` and `cat_0001.jpg` from colliding on Windows.
* Creates output files exclusively and retries with the next counter when a filename already exists. This protects existing files when multiple processes or external tools use the same output directory.
* Removes incomplete output files when Pillow fails during a save operation, without hiding the original save error.
* Truncates oversized JPEG comments only at valid UTF-8 character boundaries.
* Rejects Windows drive-relative `output_dir` values such as `C:foo`, which do not resolve beneath ComfyUI's output directory. Use an absolute path such as `C:\foo` instead.

### Tests

* Adds regression coverage for five-digit counters, case-insensitive filename matching, exclusive file creation, incomplete-file cleanup, UTF-8 comment truncation, and Windows drive-relative path rejection.

### Compatibility

No workflow migration is required. Node inputs, defaults, and directory patterns are unchanged.

## 0.1.0 - Initial release

Initial public release of **ComfyUI-PillowImageSaver**.

This release adds **Pillow Image JPEG Save**, a Pillow-based direct JPEG saver node for ComfyUI.

## Features

* Adds `Pillow Image JPEG Save`.
* Saves ComfyUI `IMAGE` tensors directly as JPEG files using Pillow.
* JPEG-only output node.
* No image preview output.
* No `IMAGE` passthrough output.
* No external command execution.
* No GraphicsMagick dependency.
* Supports organized output directory patterns.
* Supports optional `label` input for checkpoint names, experiment labels, or other workflow tags.
* Works well with `ComfyUI-CheckpointHandpickerSuite` by connecting `ckpt_name_safe` to `label`.
* Remains fully standalone and does not depend on HandpickerSuite.

## Node inputs

Required inputs:

* `images`
* `filename_prefix`
* `directory_pattern`
* `filename_date_format`
* `quality`
* `subsampling`
* `progressive`

Optional inputs:

* `output_dir`
* `label`
* `comment`

## Default settings

The initial defaults are tuned for high-volume image generation and inventory workflows.

* `filename_prefix`: `image`
* `directory_pattern`: `prefix/date`
* `filename_date_format`: `none`
* `quality`: `80`
* `subsampling`: `4:2:2`
* `progressive`: `false`

For high-quality favorite or final outputs, users can manually increase quality settings, for example:

* `quality`: `95`
* `subsampling`: `4:4:4`

## Directory patterns

Supported `directory_pattern` values:

* `none`
* `date`
* `prefix`
* `prefix_date`
* `prefix/date`
* `label`
* `label_date`
* `label/date`
* `prefix_label`
* `prefix/label`
* `prefix_label_date`
* `prefix/label/date`
* `prefix_date_label`
* `prefix/date/label`

## Filename numbering

File numbering starts with 4 digits.

Examples:

* `image_0001.jpg`
* `image_0002.jpg`
* `image_9999.jpg`
* `image_10000.jpg`

The 4-digit format is a minimum width, not a maximum limit.

## Pillow backend notes

This project is a Pillow-based sibling of `ComfyUI-GMImageSaver`.

The goal is to keep the workflow-facing behavior aligned while using Pillow instead of GraphicsMagick as the JPEG backend.

Compared with the GraphicsMagick version, this Pillow version:

* Does not require a separate GraphicsMagick installation.
* Does not call an external image processing command.
* Uses Pillow through Python package dependency management.
* Is easier to install in typical ComfyUI environments.

## Compatibility

This is the first public release.

No migration is required.
