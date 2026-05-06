# 仪表模型说明

当前仪表分支使用 `models/meter_best.pt`。该权重是 YOLOv5 旧格式模型，因此由 `meter_detector_node` 通过本地 YOLOv5 `detect.py` 调用。模型用于检测仪表关键部件，当前配置关注：

- `base`
- `start`
- `end`
- `tip`

节点会保存标注图到 `outputs/meter_annotated/`，解析 YOLOv5 `labels/*.txt`，并发布 `/vision/meter_result`。当上述关键部件足够完整时，节点根据角度比例输出估算读数。

该读数是比赛原型中的估算结果，后续可以结合具体仪表量程、刻度方向、非线性刻度和现场标定继续提升。
