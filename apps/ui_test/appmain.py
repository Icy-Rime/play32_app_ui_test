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

def main_loop():
    from ui.dialog import dialog
    from ui.progress import progress
    import gc
    from utime import sleep_ms
    def timed_task(data=[0]):
        sleep_ms(16)
        data[0] += 1
        if data[0] < 5*1000/32:
            return None, False
        elif data[0] >= 15*1000/32:
            return 1.0, True
        else:
            return (data[0]/(1000/32) - 5) / 10, False
    progress("Working...", None, timed_task, [0])
    txt = "Hello Dragon"
    ret = dialog(txt, "确认", "确认")
    dialog("You pressed {}".format("A" if ret else "B"))
    vals = [0]
    while True:
        gc.collect()
        text = "Sum:"+str(sum(vals))
        text += "\nmem:" + str(gc.mem_free())
        text += "\nSum<-5 to exit."
        ret = dialog(text, "A +1", "B -1")
        if ret == None:
            break
        if ret:
            vals[0] += 1
        else:
            vals[0] -= 1
        if vals[0] < -5:
            break
    app.reset_and_run_app("")