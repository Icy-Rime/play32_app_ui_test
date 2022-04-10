from graphic.bmfont import get_text_count

class PagedText:
    def __init__(self, text, area_w, area_h, font_w, font_h):
        pages = []
        while len(text) > 0:
            page_size = get_text_count(text, area_w, area_h, font_w, font_h)
            pages.append(text[:page_size])
            text = text[page_size:]
        if len(pages) == 0:
            pages.append("")
        self.pages = pages
        self.mark = 0
    
    def __len__(self):
        return len(self.pages)

    def get_text(self):
        return self.pages[self.mark]
    
    def page_down(self):
        np = self.mark + 1
        self.mark = self.mark if (np >= len(self.pages)) else np

    def page_up(self):
        np = self.mark - 1
        self.mark = self.mark if np < 0 else np

def draw_paged_text_with_scroll_bar(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, paged_text):
    FW, FH = font_draw.get_font_size()
    AW = frame_w - 4 # reserve for scroll bar
    offset = (AW % FW) // 2
    area_h = frame_h - 4
    font_draw.draw_on_frame(paged_text.get_text(), frame, frame_x + offset, frame_y, color_white, AW, frame_h)
    total_pages = len(paged_text)
    scroll_h = int(area_h / total_pages)
    scroll_start = int(paged_text.mark * area_h / total_pages)
    frame.fill_rect(frame_w - 3, scroll_start + 2, 2, scroll_h, color_white)
    frame.hline(frame_x + frame_w - 4, frame_y, 4, color_white)
    frame.hline(frame_x + frame_w - 4, frame_y + frame_h - 1, 4, color_white)

def draw_buttons_on_last_line(frame, frame_w, frame_h, font_draw, color_white, text_yes="YES", text_no="NO"):
    FW, FH = font_draw.get_font_size()
    HFW = FW // 2
    SINGLE = text_yes == text_no
    base_y = frame_h - FH
    mid_x = frame_w // 2
    ava_x = mid_x - FW
    # btn left
    frame.hline(0, base_y, HFW-1, color_white)
    frame.vline(0, base_y, FH, color_white)
    frame.hline(0, frame_h-1, HFW-1, color_white)
    if not SINGLE:
        # btn middle left
        frame.hline(mid_x-HFW, base_y, HFW-1, color_white)
        frame.vline(mid_x-2, base_y, FH, color_white)
        frame.hline(mid_x-HFW, frame_h-1, HFW-1, color_white)
        # btn middle right
        frame.hline(mid_x+1, base_y, HFW-1, color_white)
        frame.vline(mid_x+1, base_y, FH, color_white)
        frame.hline(mid_x+1, frame_h-1, HFW-1, color_white)
    # btn right
    frame.hline(frame_w-HFW+1, base_y, HFW-1, color_white)
    frame.vline(frame_w-1, base_y, FH, color_white)
    frame.hline(frame_w-HFW+1, frame_h-1, HFW-1, color_white)
    if SINGLE:
        tw = len(text_yes) * FW
        offset = HFW + (frame_w - FW - tw) // 2
        font_draw.draw_on_frame(text_yes, frame, offset, base_y, color_white, frame_w - FW, FH)
    else:
        tw = len(text_no) * FW
        offset = HFW + (ava_x - tw) // 2
        font_draw.draw_on_frame(text_no, frame, offset, base_y, color_white, ava_x, FH)
        tw = len(text_yes) * FW
        offset = HFW + (ava_x - tw) // 2
        font_draw.draw_on_frame(text_yes, frame, mid_x+offset, base_y, color_white, ava_x, FH)
