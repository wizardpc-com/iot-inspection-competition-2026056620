# Models

Put trained YOLO models here:

```text
models/crack_best.pt
models/meter_best.pt
models/meter_last.pt
```

`crack_best.pt` is used by `crack_detector_node`.

`meter_best.pt` is used by `meter_detector_node` for meter key-part detection. Current meter integration detects meter structure and key parts; meter reading conversion is a later extension.
