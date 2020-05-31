# Copyright (c) 2019 Gurjit Singh

# This source code is licensed under the MIT license that can be found in
# the accompanying LICENSE file or at https://opensource.org/licenses/MIT.


import argparse
import functools
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

cmdDisarm = lambda file: [
    "pdfid",
    "-d",
    "-n",
    str(file),
]

cmdDisinfect = lambda file: [
    "gs",
    "-dBATCH",
    "-dNOPAUSE",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.2",
    "-dDetectDuplicateImages=true",
    "-dDownsampleColorImages",
    "-dColorImageDownsampleType=/Bicubic",
    "-dColorImageResolution=150",
    "-dDownsampleGrayImages",
    "-dGrayImageDownsampleType=/Bicubic",
    "-dGrayImageResolution=150",
    "-dDownsampleMonoImages",
    "-dMonoImageDownsampleType=/Subsample",
    "-dMonoImageResolution=200",
    f"-sOUTPUTFILE={str(file).replace(str(file.name), f'{str(file.stem)}.disinfected.pdf')}",
    str(file),
]

getFileList = lambda ext, dirPath: [
    x
    for x in dirPath.iterdir()
    if x.is_file() and x.suffix == ".pdf" and ext not in x.name
]


def ntdExit():
    print("Nothing to do.")
    sys.exit()


def makeTargetDirs(name, dirPath):
    if not dirPath.joinpath(name).exists():
        os.mkdir(dirPath.joinpath(name))


def parseArgs():
    def dirPath(pth):
        pthObj = pathlib.Path(pth)
        if pthObj.is_dir():
            return pthObj
        else:
            raise argparse.ArgumentTypeError("Invalid Directory path")

    parser = argparse.ArgumentParser(description="Disarm/Disinfect PDF files.")

    parser.add_argument("dir", metavar="DirPath", help="Directory path", type=dirPath)
    parser.add_argument(
        "-a", "--disarm", action="store_true", help="Disarm PDF file using pdfid -d"
    )
    parser.add_argument(
        "-i",
        "--disinfect",
        action="store_true",
        help="Disinfect PDF file by printing and downsampling using GhostScript",
    )
    pargs = parser.parse_args()

    return pargs


def main(pargs):

    dirPath = pargs.dir.resolve()

    partFileList = functools.partial(getFileList, dirPath=dirPath)

    if pargs.disarm:
        fileList = partFileList(".disarmed")
    elif pargs.disinfect:
        fileList = partFileList(".disinfected")
    else:
        ntdExit()

    if not fileList:
        ntdExit()

    targetDirs = functools.partial(makeTargetDirs, dirPath=dirPath)

    targetDirs("NOT_PROCESSED")
    targetDirs("BACKUP")

    with open(dirPath.joinpath("log"), "w") as log:
        for file in fileList:
            cmd = cmdDisarm(file) if pargs.disarm else cmdDisinfect(file)

            try:
                consoleOut = (subprocess.check_output(cmd)).decode("utf-8")
            except:
                pass  # Handle This TODO

            if pargs.disinfect:
                consoleOut = re.sub(r"\n^Page\s\D*", "", consoleOut, flags=re.M)

            print("--------------------------------")
            print(consoleOut)
            log.write(f"\n{str(consoleOut)}\n")

            # print(cmd)
            # log.write(f"\n{str(cmd)}\n")

            if "PDF Header" or "Processing pages" not in consoleOut:
                shutil.move(file, dirPath.joinpath(f"NOT_PROCESSED/{file.name}"))
            else:
                shutil.move(file, dirPath.joinpath(f"BACKUP/{file.name}"))

            # time.sleep(10)
            input("\nPress Enter to continue...")


main(parseArgs())
