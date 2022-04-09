import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_RELEASE
from graphic.framebuf_helper import get_white_color
from buildin_resource.font import get_font_8px
from ui.utils import PagedText

def dialog(text="", closeable=True, loading_task=None, text_yes="OK", text_no="OK"):
    """ show a dialog and display some text.
        loading_task: () -> (text, closeable, close)
        in the loading_task function, if text == None, will not update text.
        else will reset the page and update the text.
    """
    ret = None
    for v in dialog_iter(text, closeable, loading_task, text_yes, text_no):
        ret = v
    return ret

def dialog_iter(text="", closeable=True, task=None, text_yes="OK", text_no="OK"):
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    AH = SH - FH
    paged_text = PagedText(text, SW, AH, FW, FH)
    redraw = True
    hal_keypad.clear_key_status([KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT])
    while True:
        if callable(task):
            last_closeable = closeable
            ntext, closeable, force_close = task()
            if ntext != None:
                redraw = True
                paged_text = PagedText(ntext, SW, AH, FW, FH)
            if last_closeable != closeable:
                redraw = True
            if force_close:
                yield None
                return
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_RELEASE:
                continue
            if closeable and (ekey == KEY_A or ekey == KEY_B):
                yield ekey == KEY_A
                return
            if ekey == KEY_LEFT or ekey == KEY_UP:
                paged_text.page_up()
                redraw = True
            if ekey == KEY_RIGHT or ekey == KEY_DOWN:
                paged_text.page_down()
                redraw = True
        if redraw:
            frame = hal_screen.get_framebuffer()
            frame.fill(0)
            # draw text
            F8.draw_on_frame(paged_text.get_text(), frame, 0, 0, WHITE, SW, AH)
            # draw button
            base_y = AH
            mid_x = SW // 2
            ava_x = mid_x - FW
            HFW = FW // 2
            SINGLE = text_yes == text_no
            # btn left
            frame.hline(0, base_y, HFW-1, WHITE)
            frame.vline(0, base_y, FH, WHITE)
            frame.hline(0, SH-1, HFW-1, WHITE)
            if not SINGLE:
                # btn middle left
                frame.hline(mid_x-HFW, base_y, HFW-1, WHITE)
                frame.vline(mid_x-2, base_y, FH, WHITE)
                frame.hline(mid_x-HFW, SH-1, HFW-1, WHITE)
                # btn middle right
                frame.hline(mid_x+1, base_y, HFW-1, WHITE)
                frame.vline(mid_x+1, base_y, FH, WHITE)
                frame.hline(mid_x+1, SH-1, HFW-1, WHITE)
            # btn right
            frame.hline(SW-HFW+1, base_y, HFW-1, WHITE)
            frame.vline(SW-1, base_y, FH, WHITE)
            frame.hline(SW-HFW+1, SH-1, HFW-1, WHITE)
            if closeable:
                if SINGLE:
                    tw = len(text_yes) * FW
                    offset = HFW + (SW - FW - tw) // 2
                    F8.draw_on_frame(text_yes, frame, offset, base_y, WHITE, SW - FW, FH)
                else:
                    tw = len(text_no) * FW
                    offset = HFW + (ava_x - tw) // 2
                    F8.draw_on_frame(text_no, frame, offset, base_y, WHITE, ava_x, FH)
                    tw = len(text_yes) * FW
                    offset = HFW + (ava_x - tw) // 2
                    F8.draw_on_frame(text_yes, frame, mid_x+offset, base_y, WHITE, ava_x, FH)
            else:
                if SINGLE:
                    frame.hline(HFW, base_y + (FH//2), SW - FW, WHITE)
                else:
                    frame.hline(HFW, base_y + (FH//2), mid_x - FW - 1, WHITE)
                    frame.hline(mid_x + HFW + 1, base_y + (FH//2), mid_x - FW - 1, WHITE)
            redraw = False
            hal_screen.refresh()
        if (yield None):
            return