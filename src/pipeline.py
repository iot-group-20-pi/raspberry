from __future__ import annotations

from datetime import UTC, datetime
from functools import reduce
from multiprocessing import Queue

import torch
from ultralytics.engine.results import Results

from file import FILE_DATA
from mqtt_publish import MQTT_DATA


def result_pipeline(
    result: Results,
    mqtt_q: Queue[MQTT_DATA] | None = None,
    file_q: Queue[FILE_DATA] | None = None,
    current_time: datetime | None = None,
) -> None:
    if current_time is None:
        current_time = datetime.now(tz=UTC)

    # OPTIM: remove after everything works
    if result.boxes is None or not isinstance(result.boxes.cls, torch.Tensor):
        raise TypeError(
            "The model result type mismatch, predict parameters may be wrong"
        )

    # TODO: Check if detection criteria is met
    if len(result.boxes.cls) == 0:
        return

    # ------ Send alerts
    # TODO: data format
    cls, count = result.boxes.cls.unique(return_counts=True)
    message = " ".join(
        reduce(
            lambda carry, i: carry + [f"({result.names[cls[i].item()]}:{count[i]})"],
            range(len(cls)),
            [],
        )
    )

    if mqtt_q is not None:
        mqtt_q.put(
            (
                "detection",
                f"{current_time.isoformat(timespec='microseconds')}: {message}",
            )
        )

    # ------ Save result files
    if file_q is not None:
        file_q.put(
            (
                current_time.isoformat(timespec="microseconds"),
                result.to_json(normalize=False, decimals=5),
                result.orig_img,
            )
        )
