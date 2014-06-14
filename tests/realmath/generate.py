#!/usr/bin/python

from __future__ import division
from __future__ import print_function

import sys
import random
from contextlib import contextmanager

@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target
    try:
        yield new_target
    finally:
        sys.stdout = old_target

def random_expression(depth = 3, maxparam = 0):
    def recursion():
        return random_expression(depth = depth-1, maxparam = maxparam)
    if depth == 0:
        if maxparam != 0 and random.randint(0, 1) != 0:
            return 'p%02d' % random.randint(0, maxparam-1)
        return random.choice([ '%e', '%f', '%g' ]) % random.uniform(-2, +2)
    if random.randint(0, 4) == 0:
        return recursion() + random.choice([ ' < ', ' <= ', ' == ', ' != ', ' >= ', ' > ' ]) + recursion() + ' ? ' + recursion() + ' : ' + recursion()
    op_prefix = [ '+(', '-(' ]
    op_infix = [ ' + ', ' - ', ' * ', ' / ' ]
    op_func1 = [ '$ln', '$log10', '$exp', '$sqrt', '$floor', '$ceil', '$sin', '$cos', '$tan', '$asin', '$acos', '$atan', '$sinh', '$cosh', '$tanh', '$asinh', '$acosh', '$atanh' ]
    op_func2 = [ '$pow', '$atan2', '$hypot' ]
    op = random.choice(op_prefix + op_infix + op_func1 + op_func2)
    if op in op_prefix:
        return op + recursion() + ')'
    if op in op_infix:
        return '(' + recursion() + op + recursion() + ')'
    if op in op_func1:
        return op + '(' + recursion() + ')'
    if op in op_func2:
        return op + '(' + recursion() + ', ' + recursion() + ')'
    raise

for idx in range(100): 
    with file('temp/uut_%05d.v' % idx, 'w') as f, redirect_stdout(f):
        print('module uut_%05d(output [63:0] %s);\n' % (idx, ', '.join(['y%02d' % i for i in range(100)])))
        for i in range(30):
            print('localparam p%02d = %s;' % (i, random_expression()))
        for i in range(30, 60):
            print('localparam p%02d = %s;' % (i, random_expression(maxparam = 30)))
        for i in range(100):
            print('assign y%02d = 65536 * (%s);' % (i, random_expression(maxparam = 60)))
        print('endmodule')
    with file('temp/uut_%05d.ys' % idx, 'w') as f, redirect_stdout(f):
        print('read_verilog uut_%05d.v' % idx)
        print('rename uut_%05d uut_%05d_syn' % (idx, idx))
        print('write_verilog uut_%05d_syn.v' % idx)
    with file('temp/uut_%05d_tb.v' % idx, 'w') as f, redirect_stdout(f):
        print('module uut_%05d_tb;\n' % idx)
        print('wire [63:0] %s;' % (', '.join(['r%02d' % i for i in range(100)])))
        print('wire [63:0] %s;' % (', '.join(['s%02d' % i for i in range(100)])))
        print('uut_%05d ref(%s);' % (idx, ', '.join(['r%02d' % i for i in range(100)])))
        print('uut_%05d_syn syn(%s);' % (idx, ', '.join(['s%02d' % i for i in range(100)])))
        print('task compare_ref_syn;')
        print('  input [7:0] i;')
        print('  input [63:0] r, s;')
        print('  begin')
        print('    if (-3 < $signed(r-s) && $signed(r-s) < +3)')
        print('      $display("%d: %b %b", i, r, s);')
        print('    else')
        print('      $display("%d: %b %b %s", i, r, s, r !== s ? "TRIG" : "");')
        print('  end')
        print('endtask')
        print('initial begin #1;')
        for i in range(100):
            print('  compare_ref_syn(%2d, r%02d, s%02d);' % (i, i, i))
        print('end')
        print('endmodule')
 
