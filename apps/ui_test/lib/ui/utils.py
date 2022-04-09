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
