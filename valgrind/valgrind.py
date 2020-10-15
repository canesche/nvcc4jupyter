import os
import subprocess
import tempfile
import uuid

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from common import helper

compiler = '/usr/bin/gcc'
ext = '.c'

@magics_class
class CPlugin(Magics):
    
    def __init__(self, shell):
        super(CPlugin, self).__init__(shell)
        self.argparser = helper.get_argparser()
        self.updateInstall()
    
    def updateInstall(self):
    	args = ["sh", "/content/nvcc4jupyter/valgrind/update_install.sh"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
        helper.print_out(output)
    
    def compile(self, file_path):
        args = [compiler, file_path + ext, "-o", file_path + ".out"]

        # adding flags: -O3, -unroll-loops, ...
        for flag in flags:
            if flag == "<":
                break
            args.append(flag)
        
        subprocess.check_output(args, stderr=subprocess.STDOUT)

    def run_cpp(self, file_path, args):
    	
    	self.compile(file_path)
        args = [file_path + ".out"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
            
        helper.print_out(output)

    @cell_magic
    def cachegrind(self, line, cell):
        args = line.split()
        print(args)
		
		file_path = '/content/valgrind_code'

        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_gcc(file_path, args)
        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
