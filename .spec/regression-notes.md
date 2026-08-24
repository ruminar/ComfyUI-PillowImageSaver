# Regression notes

Important points to preserve:

- Do not add output pins to the saver node.
- Do not return preview images.
- Do not add a HandpickerSuite import or shared-state dependency.
- `ckpt_name_safe` should be connected to `label` manually.
- Preserve hyphens in sanitized `label` and `filename_prefix` values.
- `label` directory patterns must raise a clear error when no label is provided.
- `directory_pattern` default must be `prefix/date`.
- JPEG defaults for the v2 family are `quality=80` and `subsampling=4:2:2`.
- `filename_date_format` applies only to filenames, not directories.
- Directory date format remains fixed `yyyyMMdd`.
- Timestamp must be captured once per node execution.
- ProgressBar should update only after each successful save.
