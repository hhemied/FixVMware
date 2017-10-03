#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 2017
@author: hhemied
Version : 0.6
"""

import os
import platform
import multiprocessing
import subprocess
import time
from shutil import copy2


dependencies = ["kernel-headers", "kernel-devel", "gcc", "dkms", "glibc-headers"]
kernel_version = platform.uname()[2]

print("""
*************FIXVMware************************************
 - Run the script on clear and update system
 - Script is compatible with Fedora systems

 - Please let me know if you face any trouble
 *********************************************************
 This script is disigned and built by Hazem Hemied(hhemied)
 **********************************************************
 """)
time.sleep(3)


# check the current login user id
def rootUser():
    # return True if root
    if os.getuid() == 0:
        return True
    else:
        print(""" Program needs root privileges to continue

         Please use [ sudo ] """)


# Testing processor virtualization compatibilities
def vmISOK():
    # processors > 2, architecture = 64bit and virtualization supported
    if multiprocessing.cpu_count() >= 2 and platform.architecture()[0] == '64bit':
        if 'vmx' or 'svm' in open('/proc/cpuinfo').read():
            return True
    else:
        print(" Your Machine is not compatible with Virtualization... ")
        return False


# Checking whether Vmware installed or not [tested with VMWare Workstation]
def vmwareInstalled():
    if os.path.exists("/usr/bin/vmware") or os.path.exists("/usr/bin/vmplayer"):
        return True
    else:
        print("VMWare is not installed...")
        return False


# Appling all steps to fix VMWARE incompitabilities with fedora systems
# and recompiling vmware modules automatically
def vmwareFix():
    if vmISOK() and vmwareInstalled():
        # Installing Necessary Packages
        print(" Installing Dependencies ...")
        for pkg in dependencies:
            cmd = subprocess.Popen('dnf install -y {}'.format(pkg), shell=True, stdout=subprocess.PIPE)

        print(" Manipulating your system files ...")
        # Copying Necessary Liberaries
        os.system('cp -r /usr/lib/vmware-installer/2.1.0/lib/lib/libexpat.so.0 /usr/lib/vmware/lib')
        os.rename('/usr/lib/vmware/lib/libz.so.1/libz.so.1', '/usr/lib/vmware/lib/libz.so.1/libz.so.1.backup')
        os.system('ln -s /usr/lib64/libz.so.1 /usr/lib/vmware/lib/libz.so.1/')
        os.chdir('/usr/lib/vmware/modules/source/')
        os.system('tar xvf vmmon.tar')
        os.system('tar xvf vmnet.tar')
        os.chdir('vmmon-only')
        os.system('make')
        os.chdir('../vmnet-only')
        os.system('make')
        os.chdir('/usr/lib/vmware/modules/source/')
        os.remove('vmmon.tar')
        os.remove('vmnet.tar')
        os.system('tar cvf vmnet.tar vmnet-only')
        os.system('tar cvf vmmon.tar vmmon-only')
        try:
            os.mkdir(os.path.join('/lib/modules/', kernel_version, 'misc'))
        # Contine if the directory exist
        except FileExistsError:
            pass
        copy2('/usr/lib/vmware/modules/source/vmmon-only/vmmon.ko', os.path.join('/lib/modules/', kernel_version, 'misc'))
        copy2('/usr/lib/vmware/modules/source/vmnet-only/vmnet.ko', os.path.join('/lib/modules/', kernel_version, 'misc/'))
        print(" Building VMWare modules ...")
        # Recompiling VMWARE modules
        os.system('depmod -a')
        print("""
        ****************************************
        Please enjoy VMware and Fedora

        Now, you can try to rerun VMware
        """)


vmwareFix()
