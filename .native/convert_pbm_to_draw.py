import os, sys
PLAY32DEV_PATH = "../../play32-dev" # replace to your path
APP_NAME_ID = "ui_test"
sys.path.append(PLAY32DEV_PATH)
import play32env
app_dir = os.path.dirname(__file__)
app_dir = os.path.abspath(os.path.join(app_dir, "..", "apps"))
# >>>> init <<<<
play32env.setup(app_dir)

# ======== start ========
from graphic import pbm, framebuf_helper
import framebuf
from sys import argv

def find_next_fg_at(frame: framebuf.FrameBuffer, x, y, iw, ih, bg_color):
    t_x = x
    while y < ih:
        while t_x < iw:
            if frame.pixel(t_x, y) != bg_color:
                return t_x, y
            t_x += 1
        y += 1
        t_x = 0
    return None

def count_same_color_h(frame: framebuf.FrameBuffer, x, y, iw, color):
    count = 0
    while x < iw:
        if frame.pixel(x, y) == color:
            count += 1
        else:
            return count
        x += 1

def count_same_color_v(frame: framebuf.FrameBuffer, x, y, ih, color):
    count = 0
    while y < ih:
        if frame.pixel(x, y) == color:
            count += 1
        else:
            return count
        y += 1

def find_max_rect_at(frame: framebuf.FrameBuffer, x, y, iw, ih):
    # return (area_size, x, y, w, h)
    color = frame.pixel(x, y)
    # h
    max_w = count_same_color_h(frame, x, y, iw, color)
    max_h = 1
    t_y = y + 1
    while t_y < ih:
        w = count_same_color_h(frame, x, t_y, iw, color)
        if w < max_w:
            break
        t_y += 1
        max_h += 1
    max_area1 = max_w * max_h, x, y, max_w, max_h
    # v
    max_w = 1
    max_h = count_same_color_v(frame, x, y, ih, color)
    t_x = x + 1
    while t_x < iw:
        h = count_same_color_v(frame, t_x, y, ih, color)
        if h < max_h:
            break
        t_x += 1
        max_w += 1
    max_area2 = max_w * max_h, x, y, max_w, max_h
    if max_area1 < max_area2:
        return max_area2
    else:
        return max_area1

def find_max_rect_in(frame: framebuf.FrameBuffer, iw, ih, bg_color):
    max_rect = None
    xy = find_next_fg_at(frame, 0, 0, iw, ih, bg_color)
    while xy != None:
        rect = find_max_rect_at(frame, xy[0], xy[1], iw, ih)
        if max_rect == None or rect[0] > max_rect[0]:
            max_rect = rect
        new_y = xy[1]
        new_x = xy[0] + rect[3]
        if new_x >= iw:
            new_x = 0
            new_y += 1
        # print(xy, rect[0], new_x, new_y)
        xy = find_next_fg_at(frame, new_x, new_y, iw, ih, bg_color)
    # print(max_rect[0]) if max_rect != None else None
    return max_rect

def split_to_rect(frame: framebuf.FrameBuffer, iw, ih):
    rect_list = []
    rect = find_max_rect_in(frame, iw, ih, 0)
    while rect != None:
        _, x, y, w, h = rect
        rect_list.append((x, y, w, h))
        frame.fill_rect(rect[1], rect[2], rect[3], rect[4], 0)
        rect = find_max_rect_in(frame, iw, ih, 0)
    return rect_list

def open_pbm(file):
    with open(file, "rb") as stream:
        iw, ih, format, data, comment = pbm.read_image(stream)
        img = framebuf.FrameBuffer(data, iw, ih, framebuf.MONO_HLSB)
    return img, iw, ih

def save_pbm(file, img):
    iw, ih = img.get_size()
    with open(file, "wb") as stream:
        pbm.make_image(stream, iw, ih, img.get_buffer(), "P4", "")

def save_py(file, rects, iw, ih):
    with open(file, "w") as f:
        f.write("def draw(frame, x, y, w, h, c):\n")
        for x, y, w, h in rects:
            # x = x / iw
            # y = y / ih
            # w = w / iw
            # h = h / ih
            x = (x - 0.5) / iw
            y = (y - 0.5) / ih
            w = (w + 0.5) / iw
            h = (h + 0.5) / ih
            f.write("    frame.fill_rect(int(x+w*{}), int(y+h*{}), int(w*{}), int(h*{}), c)\n".format(x, y, w, h))

if __name__ == "__main__":
    img, iw, ih = open_pbm(argv[1])
    img_copy = framebuf_helper.clone_framebuffer(img, iw, ih, framebuf.MONO_HLSB)
    ret = split_to_rect(img_copy, iw, ih)
    print(len(ret))
    save_py("img.py", ret, iw, ih)
    for x, y, w, h in ret:
        img_copy.rect(x, y, w, h, 1)
    save_pbm("output.pbm", img_copy)
    