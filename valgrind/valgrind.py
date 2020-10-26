import os
import subprocess
import tempfile
import uuid

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from common import helper

compiler = '/usr/bin/g++'
ext = '.cpp'

@magics_class
class ValgrindPlugin(Magics):
    
    def __init__(self, shell):
        super(ValgrindPlugin, self).__init__(shell)
        self.argparser = helper.get_argparser()
        self.already_install = False
    
    def updateInstall(self):
        print("First time use\nInstall valgrind on machine... ", end="")
        args = ["sh", "/content/nvcc4jupyter/valgrind/update_install.sh"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
        helper.print_out(output)
        print("done!")
    
    def compile(self, file_path):
        args = [compiler, file_path + ext, "-O3", "-o", file_path + ".out"]
        subprocess.check_output(args, stderr=subprocess.STDOUT)

    def run_cpp(self, file_path, args):
        
        self.compile(file_path)
        args = [file_path + ".out"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
            
        helper.print_out(output)

    @cell_magic
    def cachegrind(self, line, cell):

        if not self.already_install:
            self.already_install = True
            self.updateInstall()

        args = line.split()
        print(args)

        file_path = '/content/valgrind_code'

        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_cpp(file_path, args)
        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
