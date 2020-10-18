#!/usr/bin/env python3

import os
import pathlib
import random
import shutil
import string
import subprocess
import tempfile

ipks = []

class Ipk(object):
    "Generic ipk node."
    def __init__(self, pkgname):
        self.pkgname = pkgname
        self.deps = []
        self.version = "1.0-r1"
        self.arch = "all"
        self.maintainer = "none"
        self.description = "none"

    def add_dep(self, pkgname):
        self.deps.append(pkgname)

    def write_ipk(self):
        # Create temporary files for opkg-build
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdir = pathlib.Path(tmpdirname)

            # Make data files
            random_filename = ''.join(random.choices(string.ascii_lowercase, k=20))
            (tmpdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
            with open((tmpdir / "usr" / "bin" / random_filename), "wb") as random_file:
                random_file.write(os.urandom(100))

            # Make CONTROL file
            control_dir = (tmpdir / "CONTROL")
            control_dir.mkdir(parents=True, exist_ok=True)
            with open(control_dir / "control", "w") as control_file:
                control_file.write("Package: {}\n".format(self.pkgname))
                control_file.write("Version: {}\n".format(self.version))
                control_file.write("Architecture: {}\n".format(self.arch))
                control_file.write("Maintainer: {}\n".format(self.maintainer))
                control_file.write("Description: {}\n".format(self.description))
                deps_str = ", ".join([str(x) for x in self.deps])
                control_file.write("Depends: {}\n".format(deps_str))

            # Call opkg-build
            subprocess.run(["opkg-build", str(tmpdir)])

def create_ipk():
    next_ipk = len(ipks)
    ipk = Ipk(str(next_ipk))
    ipks.append(ipk)
    return next_ipk

def rcreate_deps(ipk, no_of_deps, max_ipks):
    """Recursively create dependencies for an ipk"""
    for i in range(0, no_of_deps):
        if len(ipks) > max_ipks:
            return

        dep = create_ipk()
        ipk.add_dep(dep)

    rcreate_deps(ipks[ipk.deps[0]], no_of_deps, max_ipks)

def main():
    # Check opkg-build is available in PATH
    shutil.which("opkg-build")

    # Generate first ipk
    ipk = create_ipk()

    # Generate 10 children for ipk
    rcreate_deps(ipks[ipk], 10, 1000)

    # Generate the ipk files
    for ipk in ipks:
        ipk.write_ipk()

if __name__ == "__main__":
    main()
