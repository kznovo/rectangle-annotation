from collections import defaultdict
import cv2


class Canvas:
    def __init__(self, filename, img_path):
        self.filename = filename
        img_array = cv2.imread(img_path)
        self.img_base = img_array
        self.img_background = img_array.copy()
        self.img_active = img_array.copy()
        self.img_show = img_array
        self.height, self.width = img_array.shape[:2]
        self.objects = set()
        self.active_sm = None
        self.active_obj = None

    def show_controller(self):
        cv2.namedWindow(self.filename)
        cv2.setMouseCallback(self.filename, self.on_mouse)

        while True:
            cv2.imshow(self.filename, self.img_show)
            key = cv2.waitKey(1) & 0xFF
            out = self.keymap[key](key - 48)
            if out:
                return out

    def labels_out(self):
        out_labels = []
        for obj in self.objects:
            obj_label = obj.label_out()
            label = [self.filename] + obj_label
            out_labels.append(label)
        return out_labels

    def destroy(self):
        cv2.destroyAllWindows()


class Painter:
    def __init__(self, canvas, draw_object, category):
        self.anchor_x = None
        self.anchor_y = None
        self.just_erased_flag = False
        self.active_cursor = 0
        self.obj = draw_object
        self.active_color = (0, 255, 0)
        self.inactive_color = (0, 100, 0)
        self.show_label = True
        self.category = category

        self.canvas = canvas
        self.canvas.on_mouse = self.on_mouse

        self.canvas.keymap = defaultdict(
            lambda: lambda *args: None,
            {
                13: self.key_enter,
                9: self.key_tab,
                8: self.key_delete,
                104: self.key_left,
                106: self.key_down,
                107: self.key_up,
                108: self.key_right,
                98: self.key_b,
                100: self.key_delete,
                110: self.key_n,
                115: self.key_s,
                113: self.key_q,
                49: self.key_numeric,
                50: self.key_numeric,
                51: self.key_numeric,
                52: self.key_numeric,
                53: self.key_numeric,
                54: self.key_numeric,
                55: self.key_numeric,
                56: self.key_numeric,
                57: self.key_numeric,
            },
        )

    def on_mouse(self, event, x, y, flags, params):
        if flags == 1:
            if event == 1:
                self.event_mouseclick(x, y)
            elif event == 0:
                self.event_mousedrag(x, y)
            elif event == 7:
                self.event_mousedblclick(x, y)
            elif event == 4:
                self.event_mouserelease(x, y)

    def draw(self):
        self.canvas.img_show = self.canvas.img_base.copy()
        for obj in self.canvas.objects:
            if obj == self.canvas.active_obj:
                self.canvas.img_show = obj.draw(self.canvas.img_show, self.active_color)
                if self.show_label:
                    self.canvas.img_show = obj.draw_category(
                        self.canvas.img_show, self.active_color
                    )
            else:
                self.canvas.img_show = obj.draw(
                    self.canvas.img_show, self.inactive_color
                )
                if self.show_label:
                    self.canvas.img_show = obj.draw_category(
                        self.canvas.img_show, self.inactive_color
                    )

    def draw_from_label(self, label):
        coords = label[2:]
        category = label[1]
        label_object = self.obj(*[float(c) for c in coords])
        label_object.category = category
        self.canvas.objects.add(label_object)
        self.canvas.img_show = self.canvas.img_base.copy()
        for obj in self.canvas.objects:
            self.canvas.img_show = obj.draw(self.canvas.img_show, self.inactive_color)
            self.canvas.img_show = obj.draw_category(
                self.canvas.img_show, self.inactive_color
            )

    def draw_active_on_background(self):
        self.canvas.img_show = self.canvas.img_background.copy()
        self.canvas.img_show = self.canvas.active_obj.draw(
            self.canvas.img_show, self.active_color
        )

    def update_background(self):
        background_obj = self.canvas.objects.copy()
        if self.canvas.active_obj:
            background_obj.remove(self.canvas.active_obj)
        self.canvas.img_background = self.canvas.img_base.copy()
        for obj in background_obj:
            self.canvas.img_background = obj.draw(
                self.canvas.img_background, self.inactive_color
            )

    def event_mouseclick(self, x, y):
        if self.just_erased_flag:
            self.just_erased_flag = False
            return

        self.anchor_x = x
        self.anchor_y = y
        for obj in self.canvas.objects:
            sm = obj.catch_sm_click(x, y)
            if sm:
                self.canvas.active_sm = sm
                self.canvas.active_obj = obj
                break
            elif obj.body.catch_click(x, y):
                self.canvas.active_obj = obj
                break
        else:
            if self.canvas.active_obj:
                self.canvas.active_obj = None
                self.draw()
            else:
                range_x = min(x, self.canvas.width - 50)
                range_y = min(y, self.canvas.height - 50)
                obj = self.obj.create_on_click(range_x, range_y)
                self.canvas.objects.add(obj)
                self.canvas.active_obj = obj
                self.draw()

        self.update_background()

    def event_mousedrag(self, x, y):
        if self.canvas.active_obj:
            sm_name = getattr(self.canvas.active_sm, "name", None)
            if sm_name:
                range_x = min(x, self.canvas.width)
                range_y = min(y, self.canvas.height)
                self.canvas.active_obj.resize(sm_name, range_x, range_y)
            else:
                add_x = x - self.anchor_x
                add_y = y - self.anchor_y
                self.canvas.active_obj.move(add_x, add_y)
                self.anchor_x = x
                self.anchor_y = y

            self.draw_active_on_background()

    def event_mouserelease(self, x, y):
        self.anchor_x = None
        self.anchor_y = None
        self.canvas.active_sm = None
        self.draw()

    def event_mousedblclick(self, x, y):
        for obj in self.canvas.objects:
            if obj.body.catch_click(x, y):
                self.canvas.objects.remove(obj)
                self.just_erased_flag = True
                self.draw()
                break

    def tab_behavior(self, ascending=True):
        if len(self.canvas.objects) > 0:
            tops = sorted(
                ((obj.get_top_coordinate(), obj) for obj in self.canvas.objects),
                key=lambda x: x[0],
            )
            if ascending:
                self.active_cursor += 1
                if len(tops) <= self.active_cursor:
                    self.active_cursor = 0
            else:
                self.active_cursor -= 1
                if self.active_cursor < 0:
                    self.active_cursor = len(tops) - 1
            self.canvas.active_obj = tops[self.active_cursor][1]

    def key_enter(self, *args):
        if self.canvas.active_obj:
            self.canvas.active_obj = None
            self.draw()

    def key_tab(self, *args):
        self.tab_behavior()
        self.draw()

    def key_delete(self, *args):
        if self.canvas.active_obj:
            self.canvas.objects.remove(self.canvas.active_obj)
            self.canvas.active_obj = None
            self.draw()

    def key_left(self, *args):
        if self.canvas.active_obj:
            self.canvas.active_obj.move(-5, 0)
            self.draw()

    def key_right(self, *args):
        if self.canvas.active_obj:
            self.canvas.active_obj.move(5, 0)
            self.draw()

    def key_up(self, *args):
        if self.canvas.active_obj:
            self.canvas.active_obj.move(0, -5)
            self.draw()

    def key_down(self, *args):
        if self.canvas.active_obj:
            self.canvas.active_obj.move(0, 5)
            self.draw()

    def key_b(self, *args):
        if self.canvas.active_obj:
            self.tab_behavior(ascending=False)
            self.draw()
        else:
            return -1

    def key_n(self, *args):
        if self.canvas.active_obj:
            self.tab_behavior(ascending=True)
            self.draw()
        else:
            return 1

    def key_s(self, *args):
        self.show_label = not self.show_label
        self.draw()

    def key_q(self, *args):
        return 2

    def key_numeric(self, key):
        if self.canvas.active_obj:
            if key in self.category:
                self.canvas.active_obj.category = self.category[key]
                self.draw()
