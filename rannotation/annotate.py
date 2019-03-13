from .helpers import CSVLabelHandler
from .label_objects import BBoxlabel
from .core import Canvas, Painter
from pathlib import Path
import json
import argparse
import sys

sys.setrecursionlimit(10 ** 9)


def interpret_signal(signal):
    """signal interpretation
    returning numbers:
        1: to the next image
        -1: previous image
        2: exit
        None: remain and do nothing
    returning sequence:
        add_page, model_inference, quit
    """
    if signal == 1:
        # next image
        return 1, False

    elif signal == 2:
        # quit
        return None, True

    elif signal == -1:
        # previous image
        return -1, False

    else:
        return 0, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img_dir")
    parser.add_argument("--csv_path")
    parser.add_argument("--labelmap_path")
    args = parser.parse_args()

    with open(args.labelmap_path, "r") as f:
        category = json.load(f)
    category = {x["id"]: x["label"] for x in category}

    img_path = list(Path(args.img_dir).glob("*.jpg"))
    img_number = 0

    while True:
        try:
            img = img_path[img_number]
        except IndexError:
            img_number = 0
            img = img_path[img_number]

        canvas = Canvas(filename=img.name, img_path=str(img))
        painter = Painter(canvas, draw_object=BBoxlabel, category=category)
        csv_label_handler = CSVLabelHandler(args.csv_path)
        csv_labels = csv_label_handler.labels_out(img.name)
        for label in csv_labels:
            painter.draw_from_label(label)

        canvas.destroy()
        signal = canvas.show_controller()
        add_page, q = interpret_signal(signal)

        new_labels = canvas.labels_out()
        csv_label_handler.overwrite(img.name, new_labels)

        if q:
            canvas.destroy()
            break

        img_number += add_page
