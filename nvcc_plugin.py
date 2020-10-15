from v1.v1 import NVCCPlugin as NVCC_V1
from v2.v2 import NVCCPluginV2 as NVCC_V2
from c.c import CPlugin as C
from cpp.cpp import CPPPlugin as CPP
from java.java import JavaPlugin as JAVA
from verilog.verilog import VERILOGPlugin as VERILOG
from gem5.gem5 import Gem5Plugin as GEM5


def load_ipython_extension(ip):
    nvcc_plugin = NVCC_V1(ip)
    ip.register_magics(nvcc_plugin)

    nvcc_plugin_v2 = NVCC_V2(ip)
    ip.register_magics(nvcc_plugin_v2)

    c_plugin = C(ip)
    ip.register_magics(c_plugin)

    cpp_plugin = CPP(ip)
    ip.register_magics(cpp_plugin)

    verilog_plugin = VERILOG(ip)
    ip.register_magics(verilog_plugin)

    java_plugin = JAVA(ip)
    ip.register_magics(java_plugin)

    gem5_plugin = GEM5(ip)
    ip.register_magics(gem5_plugin)
