# FotoVideoMover
Python 3 tools for you!

Ever had the situation where you ended up with loads of pictures/videos on your smartphone and wanted to
sort them by the creation date?

I have searched the web for a free, lightweight solution and came up with nothing fitting.

So this will help you hopefully as much as it helped me.

Just throw your media files into a folder and drop this folder onto the script.

It will scan fotos for the EXIF date and create subfolders YYYY-MM-DD and move the fotos there.

Same goes for videos. Meta info is being scanned and 'cration_date' is searched for via regex.

As this might differ for your video files, adjustments might be needed.

Therefore a 'checkmode' can be activated to see just the video metadata output so that the regex can (hopefully) easily be adjusted.

Have fun!

-> You will need to download and install FFMPEG as well as the python module ExifRead to get the code running <-
