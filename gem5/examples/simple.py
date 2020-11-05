from __future__ import print_function
from __future__ import absolute_import

# import the m5 (gem5) library created when gem5 is built
import m5
# import all of the SimObjects
from m5.objects import *

def simple_gem5(data):

	# create the system we are going to simulate
	system = System()

	# Set the clock fequency of the system (and all of its children)
	system.clk_domain = SrcClockDomain()
	system.clk_domain.clock = '1GHz'
	system.clk_domain.voltage_domain = VoltageDomain()

	# Set up the system
	system.mem_mode = 'timing'               # Use timing accesses
	system.mem_ranges = [AddrRange('512MB')] # Create an address range

	# Create a simple CPU
	system.cpu = TimingSimpleCPU()

	# Create a memory bus, a system crossbar, in this case
	system.membus = SystemXBar()

	# Hook the CPU ports up to the membus
	system.cpu.icache_port = system.membus.slave
	system.cpu.dcache_port = system.membus.slave

	# create the interrupt controller for the CPU and connect to the membus
	system.cpu.createInterruptController()

	# For x86 only, make sure the interrupts are connected to the memory
	# Note: these are directly connected to the memory bus and are not cached
	if m5.defines.buildEnv['TARGET_ISA'] == "x86":
	    system.cpu.interrupts[0].pio = system.membus.master
	    system.cpu.interrupts[0].int_master = system.membus.slave
	    system.cpu.interrupts[0].int_slave = system.membus.master

	# Create a DDR3 memory controller and connect it to the membus
	system.mem_ctrl = MemCtrl()
	system.mem_ctrl.dram = DDR3_1600_8x8()
	system.mem_ctrl.dram.range = system.mem_ranges[0]
	system.mem_ctrl.port = system.membus.master

	# Connect the system up to the membus
	system.system_port = system.membus.slave

	# get ISA for the binary to run.
	isa = str(m5.defines.buildEnv['TARGET_ISA']).lower()

	# Default to running 'hello', use the compiled ISA to find the binary
	# grab the specific path to the binary
	thispath = os.path.dirname(os.path.realpath(__file__))
	binary = os.path.join(thispath, '../../../',
		              'tests/test-progs/hello/bin/', isa, 'linux/hello')

	# Create a process for a simple "Hello World" application
	process = Process()
	# Set the command
	# cmd is a list which begins with the executable (like argv)
	process.cmd = [binary]
	# Set the cpu to use the process as its workload and create thread contexts
	system.cpu.workload = process
	system.cpu.createThreads()

	# set up the root SimObject and start the simulation
	root = Root(full_system = False, system = system)
	# instantiate all of the objects we've created above
	m5.instantiate()

	print("Beginning simulation!")
	exit_event = m5.simulate()
	print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))
