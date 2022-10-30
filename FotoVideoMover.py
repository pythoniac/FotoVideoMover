##########################################
# WHAT THIS IS FOR

# Drop a folder containing fotos and videos onto this script
# and it will try to create subfolders with the date of the
# fotos/videos and move them to these subfolders

# folder naming scheme is YYYY-MM-DD

# tested under windows7/8 x64
##########################################
# LICENSE
# this softweare is licensed unter
# GNU General Public License v3.0
# it has been originally written by pythoniac (pengo0815@gmail.com)
##########################################
# Non-standard DEPENDENCIES
# This is written in Python v3.x
# 01: EXIFREAD - - pip install ExifRead
# 02: FFPROBE - - https://ffmpeg.zeranoe.com/builds/
##########################################

# IMPORTS
import os, sys, re, shutil
from glob import glob
import subprocess as sp
from typing import Optional

try:
    import exifread
except Exception as err:
    print(f"Import error: {err}")
    print("please do " "pip install exifread" "")
    input("<return>")
    sys.exit(0)


# GLOBALS
folderList = []
FFPROBE_BIN = "ffprobe.exe"  # on Windows
extensions = ["jpg", "mp4"]  # what extensions to search for in the dropped folder
fotos = [
    "tif",
    "jpg",
    "raw",
]  # list of foto file formats - can be extended for future use
videos = [
    "avi",
    "mp4",
    "mov",
]  # same for video to let the program know what is video or foto
CHECKMODE = False  # if True: skips foto processing; switches to video and outputs results of ffprobe for debugging

# FUNCTIONS
def init() -> Optional[str]:
    if len(sys.argv) > 2:
        input("Drop only one folder at a time!\nhit <enter>")
        quit()
    elif len(sys.argv) == 1:
        input("Drop one folder at this script!\nhit <enter>")
        quit()

    path_str = str(sys.argv[1])
    if not os.path.isdir(path_str):
        input("Must be a folder not a file!\nhit <enter>")
        quit()

    print("\nFireing up on...")
    print(path_str)
    return path_str


def videoDate(fileName: str) -> Optional[str]:
    command = [FFPROBE_BIN, fileName]
    try:
        info = sp.getoutput(command)
    except sp.CalledProcessError as err:
        raise RuntimeError(
            "command '{}' returns error (code {}): {}".format(
                err.cmd, err.returncode, err.output
            )
        )

    if CHECKMODE == True:
        os.system("cls")  # for Windows
        # os.system('clear')  # for Linux/OS X
        print(fileName, "\n\n")
        print(info, "\n")
        m = re.search("creation_time.*?(\d{4}-\d{2}-\d{2})", info)
        if m:
            print("match:\n" + m.group(1))
        answer = input("\n<q> to quit or <enter> to continue: ")
        if answer.lower() in ["q"]:
            quit()
        else:
            return None

    m = re.search("creation_time.*?(\d{4}-\d{2}-\d{2})", info)
    if m:
        return str(m.group(1))
    else:
        return None


def fotoDate(fileName: str) -> Optional[str]:
    with open(fileName, "rb") as f_handle:
        tags = exifread.process_file(f_handle, stop_tag="EXIF DateTimeOriginal")

    creationDateTime = None
    try:
        creationDateTime = tags["EXIF DateTimeOriginal"]
    except KeyError:
        try:
            with open(fileName, "rb") as f_handle:
                tags = exifread.process_file(f_handle)
            creationDateTime = tags["Image DateTime"]
        except KeyError:
            for k, v in tags:
                print(f"{k}: {v}")
            input()
            
    if creationDateTime:
        creationDateTime = str(creationDateTime)
        year = creationDateTime[:4]
        month = creationDateTime[5:7]
        day = creationDateTime[8:10]
        creationDateTime = str(year + "-" + month + "-" + day)

    return creationDateTime


def folders(date):
    if date in folderList:
        return
    elif os.path.isdir(date):
        return
    else:
        os.makedirs(date)
        folderList.append(date)


# MAIN
if __name__ == "__main__":
    path = init()
    os.chdir(path)

    answer = input("\ncontinue (y = yes / c = checkmode / others abort): ")

    if not answer.lower() in ["y", "yes", "1", "c"]:
        quit()

    if answer.lower() == "c":  # checkmode is ON...
        CHECKMODE = True
        print("\n\nyou have activated checkmode!")
        print("skipping all fotos, no folder creation, no file moving")
        print("now only outputting results of ffprobe video results")
        input("hit <enter>! ")

    if CHECKMODE == False:
        print("\nprocessing EXIF\n")

    for extension in extensions:
        date = 0
        counter = 0
        extension = "*." + extension
        fileList = glob(extension)
        filesTotal = len(fileList)
        print("\n\n", filesTotal, "files for extension", extension)
        for file in fileList:
            counter += 1
            progress = 100 * counter / filesTotal

            if extension[2:] in fotos and CHECKMODE == False:
                date = fotoDate(file)
            elif extension[2:] in videos:
                date = videoDate(file)

            if date and CHECKMODE == False:
                folders(date)
                shutil.move(file, date)

            if CHECKMODE == False:
                sys.stdout.write("progress: %i%%   \r" % (progress))
                sys.stdout.flush()

    print("\n")
    input("finished - hit <enter>")
