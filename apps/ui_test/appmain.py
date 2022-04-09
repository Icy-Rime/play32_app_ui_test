import hal_screen, hal_keypad, utime
from graphic import framebuf_console, framebuf_helper
from play32sys import app
from buildin_resource.font import get_font_8px, get_font_16px
FONT_8 = get_font_8px()
FONT_16 = get_font_16px()
console = framebuf_console.Console(
    hal_screen.get_framebuffer(), *hal_screen.get_size(),
    font_draw=FONT_8,
    color=framebuf_helper.get_white_color(hal_screen.get_format()),
    display_update_fun=lambda: hal_screen.refresh()
)

def main(app_name, *args, **kws):
    hal_screen.init()
    hal_keypad.init()
    main_loop()

# count = 0
# last_now = 0
# def bg_task():
#     from utime import ticks_ms, ticks_diff
#     global count, last_now
#     now = ticks_ms()
#     if ticks_diff(now, last_now) >= 1000:
#         last_now = now
#         count += 1
#         return f"{count} secs", count >= 5, count >= 15
#     return None, count >= 5, count >= 15

def main_loop():
    from ui.dialog import dialog
    txt = "Hello World"
    # ret = dialog(txt, loading_task=bg_task, text_yes="确认", text_no="取消")
    hal_screen.get_framebuffer().fill(0)
    FONT_8.draw_on_frame("程序结束", hal_screen.get_framebuffer(), 0, 0)
    hal_screen.refresh()
    rets = []
    vals = []
    while True:
        text = "\n".join(rets[-5:])+"\n\nSum:"+str(sum(vals))
        ret = dialog(text)
        if ret == None:
            break
        if ret:
            rets.append(str(len(rets))+":+1")
            vals.append(1)
        else:
            rets.append(str(len(rets))+":-1")
            vals.append(-1)
    app.reset_and_run_app("")