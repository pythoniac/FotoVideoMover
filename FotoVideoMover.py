##########################################
# WHAT THIS IS FOR

# Drop a folder containing fotos and  onto this script
# and it will try to create subfolders with the date of the
# fotos/ and move them to these subfolders

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
folder_list = []
FFPROBE_BIN = "ffprobe.exe"  # on Windows
PIC_EXTS = [
    "tif",
    "jpg",
    "raw",
]  # list of foto file formats - can be extended for future use
VIDEO_EXTS = [
    "avi",
    "mp4",
    "mov",
]  # same for video to let the program know what is video or foto
CHECKMODE = False  # if True: skips foto processing; switches to video and outputs results of ffprobe for debugging

SCHEMAS = {
    "YMD": [
        r"threema-(\d{4})(\d{2})(\d{2})",
    ],
    "DMY": [],
}

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


def videoDate(file_name: str) -> Optional[str]:
    command = [FFPROBE_BIN, file_name]
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
        print(file_name, "\n\n")
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

    return _regex_search(file_name)


def _dt_string_from_exif(creation_dt) -> str:
    creation_dt = str(creation_dt)
    year = creation_dt[:4]
    month = creation_dt[5:7]
    day = creation_dt[8:10]
    return f"{year}-{month}-{day}"


def _regex_search(file_name: str) -> Optional[str]:
    for dt_fmt, schemas in SCHEMAS.items():
        for schema in schemas:
            if _match := re.search(schema, file_name):
                if dt_fmt == "YMD":
                    return f"{_match[1]}-{_match[2]}-{_match[3]}"
                elif dt_fmt == "DMY":
                    return f"{_match[3]}-{_match[2]}-{_match[1]}"


def fotoDate(file_name: str) -> Optional[str]:
    with open(file_name, "rb") as f_handle:
        tags = exifread.process_file(f_handle)

    try:
        creation_dt = tags["EXIF DateTimeOriginal"]
    except KeyError:
        pass
    else:
        return _dt_string_from_exif(creation_dt)

    try:
        creation_dt = tags["Image DateTime"]
    except KeyError:
        pass
    else:
        return _dt_string_from_exif(creation_dt)

    # print(f"[!] regex fallback for <{file_name}>")
    # try regex
    return _regex_search(file_name)


def folders(date):
    if date in folder_list:
        return
    elif os.path.isdir(date):
        return
    else:
        os.makedirs(date)
        folder_list.append(date)


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

    extensions = [*PIC_EXTS, *VIDEO_EXTS]
    for extension in extensions:
        date = 0
        extension = f"*.{extension}"
        file_list = glob(extension)
        files_total = len(file_list)
        print("\n\n", files_total, "files for extension", extension)
        for counter, file in enumerate(file_list, start=1):
            progress = 100 * counter / files_total

            if extension[2:] in PIC_EXTS and CHECKMODE == False:
                date = fotoDate(file)
            elif extension[2:] in VIDEO_EXTS:
                date = videoDate(file)

            if date and CHECKMODE == False:
                folders(date)
                shutil.move(file, date)

            if CHECKMODE == False:
                sys.stdout.write("progress: %i%%   \r" % (progress))
                sys.stdout.flush()

    print("\n")
    input("finished - hit <enter>")
