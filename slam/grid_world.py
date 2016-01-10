from tkinter import *
import pickle

# refresh interval (ms)
REFRESH = 1000

# BLOCK size
BLOCK = 8


class GridWorld():
    def __init__(self):
        self.master = Tk()

        self.w = Canvas(self.master, width=600, height=600)
        self.width = 600
        self.height = 600
        self.w.pack()



    def update_gridworld(self):

        try:
            ogm = pickle.load( open( "gridworld.pkl", "rb" ) )

            length = ogm.find('\n')
            width = (length+1)*BLOCK
            height = (ogm.count('\n')+2)*BLOCK

            if width != self.width or  height != self.height :
                print("CHANGE")
                old_width = self.width
                old_height = self.height
                print('width : ', old_width, " ---> ", width)
                print('height : ', old_height, " ---> ", height)

                self.w.destroy()

                self.w = Canvas(self.master, width=width, height=height)
                self.w.pack()
                self.width=width
                self.height=height
            else:
                self.w.delete(ALL)

            # w.create_line(0, 0, 200, 100)
            # w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

            #  ▁▂▃▄▅▆▇█░

            # used colors: http://www.color-hex.com/color/0000ff
            colors = {}
            colors[' '] = "#9999ff"
            colors['▁'] = "#0000ff"
            colors['▂'] = "#0000e5"
            colors['▃'] = "#0000cc"
            colors['▄'] = "#0000b2"
            colors['▅'] = "#000099"
            colors['▆'] = "#00007f"
            colors['▇'] = "#000066"
            colors['█'] = "#00004c"
            colors['░'] = "#dee3e8"

            arcs = {}
            arcs['→'] = (135, 90)
            arcs['↗'] = (180, 90)
            arcs['↑'] = (225, 90)
            arcs['↖'] = (270, 90)
            arcs['←'] = (315, 90)
            arcs['↙'] = (0, 90)
            arcs['↓'] = (45, 90)
            arcs['↘'] = (90, 90)

            x = 0
            y = 0
            cntr = 0
            for c in ogm:
                cntr += 1
                if cntr == 10000:
                    break
                if c == '\n':
                    # New grid row
                    y += BLOCK
                    x = 0
                elif c == 'X':
                    self.w.create_rectangle(x, y, x + BLOCK, y + BLOCK, fill="red")
                    x += BLOCK
                elif c in arcs:
                    # None
                    prms = arcs[c]
                    self.w.create_arc(x, y, x + BLOCK, y + BLOCK, start=prms[0], extent=prms[1], fill="red")
                    x += BLOCK
                else:
                    # draw grid cell
                    self.w.create_rectangle(x, y, x + BLOCK, y + BLOCK, fill=colors[c], width=0)
                    x += BLOCK

        except EOFError:
            # conflict with writing and reading the gridworld.pkl file
            print("try again ...")

        self.master.after(REFRESH, self.update_gridworld)

if __name__== "__main__":
    gw = GridWorld()
    gw.update_gridworld()
    gw.master.mainloop()
