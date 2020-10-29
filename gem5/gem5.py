import os
import subprocess
import tempfile
import uuid

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
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
    
    @cell_magic
    def gem5(self, line, cell="#"):
        args = line.split()
        print(args)

        file_path = '/content/gem5_code'

        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_gem5(file_path, args)
        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
