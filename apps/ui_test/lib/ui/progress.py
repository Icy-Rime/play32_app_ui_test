import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_PRESS
from graphic.framebuf_helper import get_white_color
from buildin_resource.font import get_font_8px
from ui.utils import PagedText
from utime import ticks_ms, ticks_diff

def progress(text="", progress=0.0, task=None, *args, **kws):
    """ show a progress bar with message.
        task: (*args, **kws) => (progress, force_close)
        if task return force_close == True, this function will return.
    """
    gen = progress_iter(text, progress)
    next(gen)
    if not callable(task):
        return
    while True:
        p, fc = task(*args, **kws)
        gen.send(p)
        if fc:
            return

def progress_iter(text="", progress=None):
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    AH = SH - FH
    BAR_AW = SW - 4
    BAR_AH = FH - 4
    if isinstance(text, str):
        paged_text = PagedText(text, SW, AH, FW, FH)
    else:
        paged_text = None
    running_offset = 0.0
    running_t = ticks_ms()
    while True:
        if isinstance(progress, (int, float)):
            inf = False
            if isinstance(progress, int):
                progress = progress / 100.0
        else:
            inf = True
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_LEFT or ekey == KEY_UP:
                paged_text.page_up()
                redraw = True
            if ekey == KEY_RIGHT or ekey == KEY_DOWN:
                paged_text.page_down()
                redraw = True
        # draw
        frame = hal_screen.get_framebuffer()
        frame.fill(0)
        # draw text
        if callable(text):
            text(frame, 0, 0, SW, AH, F8, WHITE)
        else:
            paged_text.draw(frame, 0, 0, SW, AH, F8, WHITE)
        # draw progress bar
        frame.rect(0, AH, SW, FH, WHITE)
        if not inf:
            bar_w = int(BAR_AW * progress)
            bar_w = min(BAR_AW, bar_w)
            bar_w = max(1, bar_w)
            frame.fill_rect(2, AH + 2, bar_w, BAR_AH, WHITE)
        else:
            now = ticks_ms()
            diff = ticks_diff(now, running_t)
            running_t = now
            running_offset = running_offset + diff * 32 / 1_000 # 32 pixel/sec
            while running_offset > FW:
                running_offset -= FW
            p_top = AH
            p_bottom = SH - 1
            off_x = FW // 2
            for x in range(-FW, SW, FW//2):
                x += int(running_offset)
                frame.line(x, p_bottom, x + off_x, p_top, WHITE)
            frame.rect(1, AH+1, SW-2, FH-2, 0)
        frame.pixel(0, AH, 0)
        frame.pixel(SW - 1, AH, 0)
        frame.pixel(0, SH - 1, 0)
        frame.pixel(SW - 1, SH - 1, 0)
        hal_screen.refresh()
        progress = (yield None)
