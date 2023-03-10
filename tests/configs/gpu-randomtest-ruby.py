#
#  Copyright (c) 2010-2015 Advanced Micro Devices, Inc.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors
#  may be used to endorse or promote products derived from this software
#  without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.

import m5
from m5.objects import *
from m5.defines import buildEnv
from m5.util import addToPath
import os, argparse, sys

m5.util.addToPath("../configs/")

from ruby import Ruby
from common import Options

parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)

# add the gpu specific options expected by the the gpu and gpu_RfO
parser.add_argument(
    "-u",
    "--num-compute-units",
    type=int,
    default=8,
    help="number of compute units in the GPU",
)
parser.add_argument(
    "--num-cp",
    type=int,
    default=0,
    help="Number of GPU Command Processors (CP)",
)
parser.add_argument(
    "--simds-per-cu", type=int, default=4, help="SIMD units" "per CU"
)
parser.add_argument(
    "--wf-size", type=int, default=64, help="Wavefront size(in workitems)"
)
parser.add_argument(
    "--wfs-per-simd",
    type=int,
    default=10,
    help="Number of " "WF slots per SIMD",
)

# Add the ruby specific and protocol specific options
Ruby.define_options(parser)

args = parser.parse_args()

#
# Set the default cache size and associativity to be very small to encourage
# races between requests and writebacks.
#
args.l1d_size = "256B"
args.l1i_size = "256B"
args.l2_size = "512B"
args.l3_size = "1kB"
args.l1d_assoc = 2
args.l1i_assoc = 2
args.l2_assoc = 2
args.l3_assoc = 2
args.num_compute_units = 8
args.num_sqc = 2

# Check to for the GPU_RfO protocol.  Other GPU protocols are non-SC and will
# not work with the Ruby random tester.
assert buildEnv["PROTOCOL"] == "GPU_RfO"

#
# create the tester and system, including ruby
#
tester = RubyTester(
    check_flush=False,
    checks_to_complete=100,
    wakeup_frequency=10,
    num_cpus=args.num_cpus,
)

# We set the testers as cpu for ruby to find the correct clock domains
# for the L1 Objects.
system = System(cpu=tester)

# Dummy voltage domain for all our clock domains
system.voltage_domain = VoltageDomain(voltage=args.sys_voltage)
system.clk_domain = SrcClockDomain(
    clock="1GHz", voltage_domain=system.voltage_domain
)

system.mem_ranges = AddrRange("256MB")

# the ruby tester reuses num_cpus to specify the
# number of cpu ports connected to the tester object, which
# is stored in system.cpu. because there is only ever one
# tester object, num_cpus is not necessarily equal to the
# size of system.cpu
cpu_list = [system.cpu] * args.num_cpus
Ruby.create_system(args, False, system, cpus=cpu_list)

# Create a separate clock domain for Ruby
system.ruby.clk_domain = SrcClockDomain(
    clock="1GHz", voltage_domain=system.voltage_domain
)

tester.num_cpus = len(system.ruby._cpu_ports)

#
# The tester is most effective when randomization is turned on and
# artifical delay is randomly inserted on messages
#
system.ruby.randomization = True

for ruby_port in system.ruby._cpu_ports:
    #
    # Tie the ruby tester ports to the ruby cpu read and write ports
    #
    if ruby_port.support_data_reqs and ruby_port.support_inst_reqs:
        tester.cpuInstDataPort = ruby_port.in_ports
    elif ruby_port.support_data_reqs:
        tester.cpuDataPort = ruby_port.in_ports
    elif ruby_port.support_inst_reqs:
        tester.cpuInstPort = ruby_port.in_ports

    # Do not automatically retry stalled Ruby requests
    ruby_port.no_retry_on_stall = True

    #
    # Tell the sequencer this is the ruby tester so that it
    # copies the subblock back to the checker
    #
    ruby_port.using_ruby_tester = True

# -----------------------
# run simulation
# -----------------------

root = Root(full_system=False, system=system)
root.system.mem_mode = "timing"
