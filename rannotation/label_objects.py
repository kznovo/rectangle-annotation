from itertools import product
import cv2


class RectangleObject:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def catch_click(self, x, y):
        return (self.xmin <= x <= self.xmax) and (self.ymin <= y <= self.ymax)

    def draw(self, img_array, color=(0, 255, 0)):
        cv2.rectangle(
            img_array,
            (int(self.xmin), int(self.ymin)),
            (int(self.xmax), int(self.ymax)),
            color,
            2,
        )
        return img_array


class CircleObject:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def catch_click(self, x, y):
        return (x - self.center_x) ** 2 + (y - self.center_y) ** 2 < self.radius ** 2

    def draw(self, img_array, color=(0, 255, 0)):
        cv2.circle(
            img_array, (int(self.center_x), int(
                self.center_y)), self.radius, color, 2
        )
        return img_array


class BBoxlabel:
    def __init__(self, xmin, ymin, xmax, ymax, category=None):
        self.body = RectangleObject(xmin, ymin, xmax, ymax)
        self.category = category or "unspecified"
        self.update_sm()

    def update_sm(self):
        self.sm = set()
        sm_names = ["LT", "LM", "LB", "MT", "MB", "RT", "RM", "RB"]
        x = (
            self.body.xmin,
            self.body.xmin + (self.body.xmax - self.body.xmin) / 2,
            self.body.xmax,
        )
        y = (
            self.body.ymin,
            self.body.ymin + (self.body.ymax - self.body.ymin) / 2,
            self.body.ymax,
        )
        sm_coords = list(product(x, y))
        del sm_coords[4]  # center xy
        for (cx, cy), name in zip(sm_coords, sm_names):
            sm = CircleObject(cx, cy, radius=4)
            sm.name = name
            self.sm.add(sm)

    def catch_sm_click(self, x, y):
        for sm in self.sm:
            if sm.catch_click(x, y):
                return sm

    def draw(self, img_array, color=(0, 255, 0)):
        img_array = self.body.draw(img_array, color)
        for sm in self.sm:
            img_array = sm.draw(img_array, color)
        return img_array

    def get_top_coordinate(self):
        return self.body.ymin

    def draw_category(self, img_array, color=(0, 255, 0)):
        text_top = (self.body.xmin, self.body.ymin - 10)
        text_bot = (self.body.xmin + 80, self.body.ymin + 5)
        text_pos = (self.body.xmin + 5, self.body.ymin)
        cv2.rectangle(
            img_array, tuple(map(int, text_top)), tuple(
                map(int, text_bot)), color, -1
        )
        cv2.putText(
            img_array,
            self.category,
            tuple(map(int, text_pos)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 0),
            1,
        )
        return img_array

    def label_out(self):
        return [
            self.category,
            self.body.xmin,
            self.body.ymin,
            self.body.xmax,
            self.body.ymax,
        ]

    @classmethod
    def create_on_click(cls, x, y):
        return cls(x - 25, y - 25, x + 25, y + 25)

    def resize(self, sm_name, x, y):
        if sm_name in ("LT", "LM", "LB"):
            self.body.xmin = min(x, self.body.xmax - 1)
        elif sm_name in ("RT", "RM", "RB"):
            self.body.xmax = max(x, self.body.xmin + 1)

        if sm_name in ("LT", "MT", "RT"):
            self.body.ymin = min(y, self.body.xmax - 1)
        elif sm_name in ("LB", "MB", "RB"):
            self.body.ymax = max(y, self.body.ymin + 1)

        self.update_sm()

    def move(self, add_x, add_y):
        self.body.xmin += add_x
        self.body.xmax += add_x
        self.body.ymin += add_y
        self.body.ymax += add_y
        self.update_sm()
