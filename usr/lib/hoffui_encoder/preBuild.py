"""
HoffUI FFMPEG Encoder - Pre-Build Development Utility

This utility module is used during the development and build process to toggle
the DEBUG flag in the Functions module. It automatically sets DEBUG to False
for production builds while allowing developers to maintain debugging capabilities
during development.

Author: Brad Heffernan
Email: brad.heffernan83@outlook.com
Project: HoffUI Encoder
License: GNU General Public License v3.0

Usage:
- Run during build process to disable debug mode for production
- Automatically modifies Functions.py to set DEBUG = False
- Ensures clean production builds without debug output
- Part of the automated build pipeline

Dependencies:
- pathlib: Modern file path handling
- File I/O operations for Functions.py modification
"""

from pathlib import Path

paths = str(Path(__file__).parents[0])


class PreBuild:
    def __init__(self):
        super(PreBuild, self).__init__()
        self.old = ""
        self.lines = []
        self.new = "False"

        self.readLines()
        self.writeLines()

    def _getPosition(self, file, text):
        nlist = [x for x in file if text in x]
        print(paths + "\\Functions.py")
        position = file.index(nlist[0])
        return position

    def readLines(self):
        with open(paths + "\\Functions.py", "r") as f:
            self.lines = f.readlines()
            pos = self._getPosition(self.lines, "DEBUG =")
            line = self.lines[pos]
            self.old = line.split("=")[1].strip()
            f.close()

    def writeLines(self):
        with open(paths + "\\Functions.py", "w") as w:
            pos = self._getPosition(self.lines, "DEBUG =")

            self.lines[pos] = self.lines[pos].replace(self.old, self.new)

            w.writelines(self.lines)
            w.close()


if __name__ == "__main__":
    PreBuild()
