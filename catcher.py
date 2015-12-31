#!/usr/bin/env python

import argparse, hashlib, os, shutil, sys, tarfile, tempfile

parser = argparse.ArgumentParser(description='Receive and install files from a zipfile.')
parser.add_argument('--validate', dest='validate_command', action='store',
                   help='shell command to validate config before proceeding')
parser.add_argument('--reload', dest='reload_command', action='store',
                   help='shell command to execute after received file tree is installed')
parser.add_argument('target', type=str, nargs=1,
                   help='location to install received file tree')
parser.add_argument('-v', dest='verbose', action='store_true',
                   help='verbose output')
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
    if args.verbose: print 'Executing %s' % cmd
    res = os.system(cmd)
    if res > 0:
        print >> sys.stderr, 'Validation failed - aborting'
        sys.exit(1)

backup = os.path.join(tempfile.gettempdir(), target.replace('/', '_'))
if os.path.exists(backup):
    print >> sys.stderr, 'Backup %s left from previous run. Please clean up.' % backup
    sys.exit(1)

# First, a backup
shutil.copytree(target, backup)

# Clean target directory without actually deleting target dir itself
for entry in os.listdir(target):
    dst = os.path.join(target, entry)
    if args.verbose: print 'Removing existing %s' % dst
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        os.remove(dst)

# Install the contents of tarfile into target dir
for entry in os.listdir(temp):
    src = os.path.join(temp, entry)
    dst = os.path.join(target, entry)
    if args.verbose: print 'Installing %s' % dst
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

if args.reload_command:
    res = os.system(args.reload_command)
    if res > 0:
        print >> sys.stderr, 'Reload failed'
        sys.exit(res)

shutil.rmtree(backup)
