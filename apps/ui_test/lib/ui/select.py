import hal_screen, hal_keypad
from hal_keypad import parse_key_event, KEY_A, KEY_B, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, EVENT_KEY_PRESS
from graphic.framebuf_helper import get_white_color
from buildin_resource.font import get_font_8px
from ui.utils import PagedText, draw_buttons_at_last_line, draw_label_nav
from machine import lightsleep
from play32hw.cpu import cpu_speed_context, VERY_SLOW, FAST

def select_menu(text="", options=[], text_yes="YES", text_no="NO"):
    """ show a menu and display some text.
        select_menu has a big area to display text, it is suitable for explaining your options.
    """
    with cpu_speed_context(VERY_SLOW):
        for v in select_menu_iter(text, options, text_yes, text_no):
            if v != None:
                return v
            lightsleep(33) # save power

def select_menu_iter(text="", options=[], text_yes="YES", text_no="NO"):
    WHITE = get_white_color(hal_screen.get_format())
    SW, SH = hal_screen.get_size()
    F8 = get_font_8px()
    FW, FH = F8.get_font_size()
    AH = SH - FH - FH
    OP_SIZE = len(options)
    if isinstance(text, str):
        paged_text = PagedText(text, SW, AH, FW, FH)
    else:
        paged_text = None
    pointer = 0
    redraw = True
    while True:
        for event in hal_keypad.get_key_event():
            etype, ekey = parse_key_event(event)
            if etype != EVENT_KEY_PRESS:
                continue
            if ekey == KEY_A or ekey == KEY_B:
                yield pointer if ekey == KEY_A and OP_SIZE > 0 else -1 - pointer
            if ekey == KEY_UP:
                paged_text.page_up()
                redraw = True
            if ekey == KEY_DOWN:
                paged_text.page_down()
                redraw = True
            if OP_SIZE > 0 and ekey == KEY_LEFT:
                pointer -= 1
                pointer %= OP_SIZE
                redraw = True
            if OP_SIZE > 0 and ekey == KEY_RIGHT:
                pointer += 1
                pointer %= OP_SIZE
                redraw = True
        if redraw:
            with cpu_speed_context(FAST):
                frame = hal_screen.get_framebuffer()
                frame.fill(0)
                # draw text
                if callable(text):
                    text(frame, 0, 0, SW, AH, F8, WHITE)
                else:
                    paged_text.draw(frame, 0, 0, SW, AH, F8, WHITE)
                # draw options
                if OP_SIZE > 0:
                    draw_label_nav(frame, 0, AH, SW, FH, F8, WHITE, options[pointer])
                # draw button
                draw_buttons_at_last_line(frame, SW, SH, F8, WHITE, text_yes, text_no)
                redraw = False
                hal_screen.refresh()
        yield None
