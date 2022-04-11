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


def progress_timed_task(data=[0]):
    utime.sleep_ms(8) # this is inaccuracy, use ticks_diff and ticks_add.
    data[0] += 1
    if data[0] < 5*1000/32:
        return None, False
    elif data[0] >= 15*1000/32:
        return 1.0, True
    else:
        return (data[0]/(1000/32) - 5) / 10, False

MENU = """Select an UI to see what it looks like.


呀！隐藏页被发现了！那就给你看看吧~
龙（Dragons）是《冰与火之歌》中虚构的一种魔法物种，跟许多奇幻小说中龙的虚构形象类似。权力的游戏刚开始人们都相信龙已经灭绝，到该卷结尾的时候，冰与火之歌的世界中再一次出现了龙。
"""

def main_loop():
    from ui.select import select_menu, select_list
    from ui.dialog import dialog
    from ui.progress import progress
    import gc
    select_list("Menu", ["Progress", "Dialog", "========", "tester", "Dragon", "Wyvern", "Kobold"])
    while True:
        ret = select_menu(MENU, "Main Menu", ["Progress", "Dialog"], text_yes="ENTER", text_no="EXIT")
        if ret < 0:
            break
        elif ret == 0:
            progress("Working...\nPlease wait.", "Progress", None, progress_timed_task, [0])
        elif ret == 1:
            dg_ret = dialog("Press A or B.", "Dialog", "Press", "Press")
            dialog("You pressed {}".format("A" if ret else "B"))
            vals = [0]
            while True:
                gc.collect()
                text = "Sum:"+str(sum(vals))
                text += "\nmem:" + str(gc.mem_free())
                text += "\nSum<-5 to exit."
                dg_ret = dialog(text, "Add Em All", "A +1", "B -1")
                if dg_ret:
                    vals[0] += 1
                else:
                    vals[0] -= 1
                if vals[0] < -5:
                    break
    app.reset_and_run_app("")