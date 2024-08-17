import os, sys, cpuinfo, torch

def cpu_is_x86() -> bool:
    '''Returns whether the CPU architecture is x86.'''
    info = cpuinfo.get_cpu_info()
    return info['arch'] == 'X86_64'

def cpu_is_arm() -> bool:
    '''Returns whether the CPU architecture is ARM.'''
    info = cpuinfo.get_cpu_info()
    return info['arch'] == 'ARM'

def cpu_supports_avx2() -> bool:
    '''Returns whether the CPU supports AVX2 instructions.'''
    info = cpuinfo.get_cpu_info()
    return 'avx2' in info['flags']

def system_has_gpu() -> bool:
    '''Returns whether the system has a GPU.'''
    return torch.cuda.is_available()