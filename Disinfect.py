# Copyright (c) 2020 Gurjit Singh

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
    sys.executable,
    pathlib.Path(__file__).parents[0].resolve().joinpath("./pdfid/pdfid.py"),
    "-d",
    "-n",
    str(file),
]

cmdDisinfect = lambda file: [
    "gs.exe",  # or gs
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

bytesToMB = lambda bytes: round(bytes / float(1 << 20), 3)

getTimeStr = lambda: time.strftime("%d-%m-%y_%H-%M-%S")


def printLog(data, logRef):
    print(data)
    logRef.write(data)


def ntdExit():
    print("Nothing to do.")
    sys.exit()


def makeTargetDirs(name, dirPath):
    if not dirPath.joinpath(name).exists():
        os.mkdir(dirPath.joinpath(name))


def waitN(n):
    print("\n")
    for i in reversed(range(0, n)):
        print(
            f"Waiting for {str(i).zfill(3)} seconds.", end="\r", flush=True
        )  # padding for clearing digits left from multi digit coundown
        time.sleep(1)
    print("\r")


def parseArgs():
    def dirPath(pth):
        pthObj = pathlib.Path(pth)
        if pthObj.is_dir():
            return pthObj
        else:
            raise argparse.ArgumentTypeError("Invalid Directory path")

    parser = argparse.ArgumentParser(
        description="Disarm/Disinfect PDF files using PDFiD and GhostScript."
    )
    parser.add_argument(
        "-d", "--dir", required=True, help="Directory path", type=dirPath
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-a", "--disarm", action="store_true", help="Disarm PDF file using pdfid -d"
    )
    group.add_argument(
        "-i",
        "--disinfect",
        action="store_true",
        help="Disinfect PDF file by printing and downsampling using GhostScript",
    )
    parser.add_argument(
        "-w",
        "--wait",
        nargs="?",
        default=None,
        const=4,
        type=int,
        help="Wait time in seconds between each iteration, default is 4",
    )
    pargs = parser.parse_args()

    return pargs


def main(pargs):

    dirPath = pargs.dir.resolve()

    partFileList = functools.partial(getFileList, dirPath=dirPath)

    if pargs.disarm:
        fileList = partFileList(".disarmed")
        logname = "log.disarmed"
        validCheck = "PDF Header:"

    elif pargs.disinfect:
        fileList = partFileList(".disinfected")
        logname = "log.disinfected"
        validCheck = "Processing pages "

    else:
        ntdExit()

    if not fileList:
        ntdExit()

    targetDirs = functools.partial(makeTargetDirs, dirPath=dirPath)

    targetDirs("NOT_PROCESSED")
    targetDirs("BACKUP")

    oldSize = totalOldSize = 0
    newSize = totalNewSize = 0

    with open(dirPath.joinpath(f"{logname}_{getTimeStr()}"), "w") as log:
        for i, file in enumerate(fileList):
            cmd = cmdDisarm(file) if pargs.disarm else cmdDisinfect(file)

            oldSize = file.stat().st_size
            totalOldSize += oldSize
            printLogP = functools.partial(printLog, logRef=log)

            printLogP("\n================================")
            printLogP(f"\n{i + 1}/{len(fileList)} - {getTimeStr()}")
            printLogP(f"\n{str(file.name)}\n")

            try:
                consoleOut = (subprocess.check_output(cmd)).decode("utf-8")
            except:
                printLogP(
                    f"can't run {cmd[0]}"
                )  # needs fixing doesnt move file to not processed
                continue  # TODO: Handle This

            if pargs.disinfect:
                consoleOut = re.sub(r"\n^Page\s\D*", "", consoleOut, flags=re.M)
                newSize = os.stat(cmd[-2].replace("-sOUTPUTFILE=", "")).st_size
                totalNewSize += newSize

            printLogP("\n--------------------------------")
            printLogP(f"\n{str(consoleOut)}\n")

            if validCheck not in str(consoleOut):
                shutil.move(file, dirPath.joinpath(f"NOT_PROCESSED/{file.name}"))
                printLogP(f"{file.name} moved to ./NOT_PROCESSED/ directory")
            else:
                shutil.move(file, dirPath.joinpath(f"BACKUP/{file.name}"))
                printLogP(f"Source file: {file.name} moved to ./BACKUP/ directory")

            if pargs.disinfect:
                if newSize > (oldSize * 2):
                    printLogP(
                        "\nResulting file is significantly larger than the source file."
                    )

                printLogP(
                    f"\nOld size: {bytesToMB(oldSize)} MB\nNew Size :{bytesToMB(newSize)} MB\n"
                )

            # time.sleep(10)
            if pargs.wait:
                waitN(int(pargs.wait))
            # input("\nPress Enter to continue...")

        if pargs.disinfect:
            printLogP(
                f"\nTotal Old size: {bytesToMB(oldSize)} MB\nTotal New Size :{bytesToMB(newSize)} MB\n"
            )


main(parseArgs())
