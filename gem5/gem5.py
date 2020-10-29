import os
import subprocess
import tempfile
import uuid

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import *
from common import helper

ext = '.py'

@magics_class
class Gem5Plugin(Magics):
    
    def __init__(self, shell):
        super(Gem5Plugin, self).__init__(shell)
        self.argparser = helper.get_argparser()
        #self.updateInstall()
    
    def updateInstall(self):
        print("Install dependencies Gem5... ", end="")
        args = ["sh", "/content/nvcc4jupyter/valgrind/update_install.sh"]

        self.execution(args)
        print("done!")
    
    def execution(self, args):
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
        helper.print_out(output)

    def run_gem5(self, file_path, args):

        arguments = ["sh", "/content/nvcc4jupyter/gem5/execute.sh", args[0], file_path + ext]

        self.execution(arguments)

        if len(args) > 1:
            if 'all' in args[1:]:
                arguments = ["cat", "/content/m5out/stats.txt"]
                self.execution(arguments)
            else:
                print("---------- Begin Simulation Statistics ----------")
                for s in args[1:]:
                    arguments = ["sh", "/content/nvcc4jupyter/gem5/statistic.sh", s]
                    output = subprocess.check_output(args, stderr=subprocess.STDOUT)
                    output = output.decode('utf8')
                    helper.print_out(output.replace("\n\n","\n"))

    def view_scope(self):

        def on_button_clicked(b):
            print("Button clicked.", b.description)

        def on_value_change(change):
            print(change['owner'].name)

        def create_expanded_button(description, button_style=""):
            btn = Button(description=description, button_style=button_style, layout=Layout(height='auto', width='auto'))
            btn.on_click(on_button_clicked)
            return btn

        def create_expanded_slider(id, description="", button_style="", min=1, max=10, value=1, step=1):
            slider = IntSlider(description="", button_style=button_style, layout=Layout(height='auto', width='auto'), min=min, max=max, value=value, step=step)
            slider.observe(on_value_change, names='value')
            slider.name = id
            return slider
        def create_expanded_intText(description="", button_style="", min=1, max=10, value=1, step=1):
            return BoundedIntText(description=description, button_style=button_style, layout=Layout(height='auto', width='auto'), min=min, max=max, value=value, step=step)
        def create_expanded_floatText(description="", button_style="", min=1, max=10, value=1, step=1):
            return BoundedFloatText(description=description, button_style=button_style, layout=Layout(height='auto', width='auto'), min=min, max=max, value=value, step=step)
        def create_expanded_Select(description="", button_style="", value=0, options=[]):
            return Select(description=description, button_style=button_style, layout=Layout(height='40px', width='auto'), value=value, options=options)

        # create a 10x2 grid layout
        grid = GridspecLayout(2, 10)
        # fill it in with widgets
        grid[0, 0] = create_expanded_button("Architecture", "warning")
        grid[0, 1] = create_expanded_button("X86")
        grid[0, 2] = create_expanded_button("RiscV")
        grid[0, 3] = create_expanded_button("Arm")
        grid[1, 0] = create_expanded_button("CPU", "warning")
        grid[1, 1] = create_expanded_button("Simple")
        grid[1, 2] = create_expanded_button("In Order")
        grid[1, 3] = create_expanded_button("Out Order")

        gridclock = GridspecLayout(1, 10)
        gridclock[0,0] = create_expanded_button("Clock (GHz)", "warning")
        gridclock[0,1] = create_expanded_floatText(value=2.0, min=0.1, max=5.0, step=1)

        gridCache = GridspecLayout(2, 10)
        gridCache[0,0] = create_expanded_button("Cache", "warning")
        gridCache[0,1] = create_expanded_button("Size (kB)", "warning")
        gridCache[0,2] = create_expanded_button("Associative", "warning")
        #gridCache[0,3] = create_expanded_button("tag_latency", "warning")
        gridCache[0,3] = create_expanded_button("data_latency", "warning")
        #gridCache[0,4] = create_expanded_button("resp_latency", "warning")
        gridCache[0,4] = create_expanded_button("mshrs", "warning")
        gridCache[0,5] = create_expanded_button("tgts_per_mshr", "warning")
        gridCache[1,0] = create_expanded_button("L1Cache", "warning")
        gridCache[1,1] = create_expanded_intText(value=16, max=2048, step=2)
        gridCache[1,2] = create_expanded_slider("assoc", value=2, min=2, max=10, step=2)
        #gridCache[1,3] = create_expanded_slider(value=2)
        gridCache[1,3] = create_expanded_slider("data_latency", value=2)
        #gridCache[1,4] = create_expanded_slider(value=2)
        gridCache[1,4] = create_expanded_slider("mshrs", value=4)
        gridCache[1,5] = create_expanded_slider("tgts_per_mshr", value=20, min=10, max=50)

        gridCacheL2 = GridspecLayout(1, 10)

        gridCacheL2[0,0] = create_expanded_button("L2Cache", "warning")
        gridCacheL2[0,1] = create_expanded_floatText(value=256, max=2048, step=2)
        gridCacheL2[0,2] = create_expanded_slider("", value=8)
        #gridCacheL2[0,3] = create_expanded_slider(value=20, max=40)
        gridCacheL2[0,3] = create_expanded_slider("", value=20, max=40)
        #gridCacheL2[0,4] = create_expanded_slider(value=20, max=40)
        gridCacheL2[0,4] = create_expanded_slider("", value=20, max=40)
        gridCacheL2[0,5] = create_expanded_slider("", value=12, min=10, max=50)

        gridMemory = GridspecLayout(1, 10)
        gridMemory[0,0] = create_expanded_button("Memory", "warning")
        gridMemory[0,1] = create_expanded_Select("", options=['DDR3_1600_8x8','DDR4_2400_8x8'], value='DDR3_1600_8x8')

        gridSim = GridspecLayout(1, 10)
        #danger = vermelho
        gridSim[0,0] = create_expanded_button("Start Simulate", "success")

        display(grid)
        display(gridclock)
        print("")
        display(gridCache)
        display(gridCacheL2)
        print("")
        display(gridMemory)
        print("")
        display(gridSim)
    
    @cell_magic
    def gem5(self, line, cell):
        args = line.split()
        
        if 'visual' in line:
            self.view_scope()
            return

        file_path = '/content/gem5_code'

        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_gem5(file_path, args)
        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
