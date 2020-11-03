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
        print("Installing valgrind. Please wait... ", end="")
        args = ["sh", "/content/nvcc4jupyter/valgrind/update_install.sh"]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')
        #helper.print_out(output)
        print("done!")
    
    def parse_out(self, out, print_file):
        c = 0
        if print_file:
            f = open("/content/print_out.txt", "w")

        for l in out.split('\n'):
            if c > 12:
                res = l.split("==")
                if len(res) > 1:
                    print(res[2][1:])
                    if print_file:
                        f.write(res[2][1:] + "\n")
            c += 1
    
    def parse_res(self, out, results):
        c = 0
        for l in out.split('\n'):
            if c > 12:
                res = l.split("==")
                if len(res) > 1:
                    if 'D1  misses:' in res[2][1:]:
                        value = res[2][1:].split(":")[1].split("(")[0].replace(",","").replace(" ","")
                        results['misses'] = int(value)
                    elif 'D1  miss rate:' in res[2][1:]:
                        value = res[2][1:].split(":")[1].split("(")[0].replace(",","").replace(" ","")
                        results['miss_rate'] = int(value)
            c += 1
        print(results)

    def exec_range_cache(self, args, results):

        v = '--D1=%d,%d,%d' %(args[0]*1024,args[1],args[2])
        args = ["sh", "/content/nvcc4jupyter/valgrind/execute.sh", v, '', '']

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')

        self.parse_res(output, results)

    def executeValgrind(self, args, print_file):

        v = ['', '', '']

        for i in range(len(args)):
            if i >= 3:
                break
            v[i] = args[i]

        args = ["sh", "/content/nvcc4jupyter/valgrind/execute.sh", v[0], v[1], v[2]]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        output = output.decode('utf8')

        self.parse_out(output, print_file)
    
    def compile(self, file_path):
        args = [compiler, file_path + ext, "-o", file_path + ".out"]
        subprocess.check_output(args, stderr=subprocess.STDOUT)

    def run_cpp(self, file_path):
        
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

        print_file = False
        if '--file' in line:
            line.replace("--file", "")
            print_file = True

        args = line.split()

        file_path = '/content/valgrind_code'

        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_cpp(file_path)
            self.executeValgrind(args, print_file)

        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
    
    @cell_magic
    def rangecachegrind(self, line, cell):

        if not self.already_install:
            self.already_install = True
            self.updateInstall()

        datacache = [4]
        ways = [2]
        lines = [32]
        bargraph = ['misses', 'miss_rate']

        line = line.strip().replace(" ","").split(";")
        print(line)

        for l in line:
            if 'datacache' in l:
                datacache = []
                l = l.replace('datacache=','').replace('(','').replace(')','').split(',')
                print(l)
                for d in l:
                    print(d)
                    datacache.append(int(d))
            elif 'ways' in l:
                ways = []
                l = l.replace('ways=','').replace('(','').replace(')','').split(',')
                for d in l:
                    ways.append(int(d))
            elif 'line' in l:
                lines = []
                l = l.replace('line=','').replace('(','').replace(')','').split(',')
                for d in l:
                    lines.append(int(d))
            elif 'bargraph' in l:
                bargraph = []
                l = l.replace('bargraph=','').replace('(','').replace(')','').split(',')
                for d in l:
                    bargraph.append(d)

        print(datacache, ways, lines, bargraph)        

        file_path = '/content/valgrind_code'

        with open(file_path + ext, "w") as f:
            f.write(cell)
        try:
            self.run_cpp(file_path)
            
            results = {}
            for b in bargraph:
                results[b] = []

            for i in range(len(datacache)):
                for j in range(len(ways)):
                    for k in range(len(lines)):
                        args = [datacache[i], ways[j], lines[k]]
                        self.exec_range_cache(args, results)

            print(results)

        except subprocess.CalledProcessError as e:
            helper.print_out(e.output.decode("utf8"))
