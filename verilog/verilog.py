import os
import subprocess
import tempfile
import uuid
import graphviz
from IPython.display import display, Image
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from common import helper

compiler = '/content/nvcc4jupyter/verilog/bin/iverilog'
yosys_run = '/content/nvcc4jupyter/verilog/yosys'
script_run = '/content/nvcc4jupyter/verilog/script.ys'
ext = '.v'

@magics_class
class VERILOGPlugin(Magics):
    
    def __init__(self, shell):
        super(VERILOGPlugin, self).__init__(shell)
        self.argparser = helper.get_argparser()
        self.permission()
    
    def permission(self):
        args = ["chmod", "a+x", "-R", "/content/nvcc4jupyter/verilog/"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')

    @staticmethod
    def compile(file_path, flags):
        args = [compiler, file_path + ext, "-o", file_path + ".out"]

        # adding flags: -O3, -unroll-loops, ...
        for flag in flags:
            if flag == "<":
                break
            args.append(flag)
        
        subprocess.check_output(args, stderr=subprocess.STDOUT)

    def run_verilog(self, file_path):
        args = [file_path + ".out"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
            
        helper.print_out(output)
    
    def run_yosys(self, file_path):
        args = [yosys_run, "-Q", "-T", "-q", "-s", script_run]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
        helper.print_out(output)

        # Printer dot
        display(Image(filename="/content/code.png"))
    
    def run_waveform(self, path):

        args = ['python3', path]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')

        eval(path)
        #helper.print_out(output)

    @cell_magic
    def verilog(self, line, cell):
        args = line.split()

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, str(uuid.uuid4()))
            with open(file_path + ext, "w") as f:
                f.write(cell)
            try:
                self.compile(file_path, args)
                self.run_verilog(file_path)
            except subprocess.CalledProcessError as e:
                helper.print_out(e.output.decode("utf8"))
    
    @cell_magic
    def print_verilog(self, line, cell):
        args = line.split()

        file_path = os.path.join('/content/code')
        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_yosys(file_path)
        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
    
    @cell_magic
    def waveform(self, line, cell):
        args = line.split()

        name = 'out.vcd'
        if len(args) > 0:
            name = args[0]
            if '.vcd' not in name:
                name += '.vcd'

        file_path = os.path.join('/content/execute.py')

        with open(file_path, "w") as f:
            f.write("import sys\n")
            f.write("sys.path.insert(0,'.')\n")
            f.write("from nvcc4jupyter.verilog.vcd_parser.vcd_plotter import VcdPlotter\n")
            f.write("vcd_plt  = VcdPlotter('/content/%s')\n" %name)
            f.write(cell)
            f.write("vcd_plt.show(sign_list, time_begin, time_end, base)\n")
        try:
            self.run_waveform(file_path)
        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))