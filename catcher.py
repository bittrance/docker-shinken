#!/usr/bin/env python

import argparse, hashlib, os, shutil, sys, tarfile, tempfile

parser = argparse.ArgumentParser(description='Receive and install files from a zipfile.')
parser.add_argument('--validate', dest='validate_command', action='store',
                   help='shell command to validate config before proceeding')
parser.add_argument('--reload', dest='reload_command', action='store',
                   help='shell command to execute after received file tree is installed')
parser.add_argument('target', type=str, nargs=1,
                   help='location to install received file tree')
args = parser.parse_args()

target = args.target[0]
if not os.path.exists(target):
    print 'target dir %s does not exist' % target
    sys.exit(1)

if args.validate_command and '{}' not in args.validate_command:
    args.validate_command += ' {}'

fd = tempfile.NamedTemporaryFile()
while True:
    data = sys.stdin.read(8192)
    if not data:
        break
    fd.write(data)
fd.seek(0)

temp = tempfile.mkdtemp()
tar = tarfile.open(fileobj=fd, mode='r|*')
tar.extractall(path=temp)

if args.validate_command:
    cmd = args.validate_command
    cmd = cmd.replace('{}', temp)
    res = os.system(cmd)
    if res > 0:
        print 'Validation failed - aborting'
        sys.exit(1)

shutil.move(target, target + '.old')
shutil.move(temp, target)

if args.reload_command:
    res = os.system(args.reload_command)
    if res > 0:
        print 'Reload failed'
        sys.exit(res)
