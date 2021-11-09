You will need to be running Tesseract OCR on the hosting machine: https://github.com/tesseract-ocr/tesseract
You may have to change the directory in line 9 of OCR.py to point to the tesseract exe

Run backend.py and navigate to http://127.0.0.1:5000/ to use it on the host machine

Let me know if anything breaks for you and I can troubleshoot

Schedule images should be head on and somewhat well-lit, but they can be cropped via the program.
Google login may be buggy, delete your token if there is an issue and login again

Agreed upon docs to be submitted are in the "Project Submissions" folder
Video recording does not show other windows so it may look like nothing happened, I was usually dropping in an image or selecting the start date.

Potential improvements:
Multiple filters until it reads the best result
Impliment cookies (sessions seem like they don't apply to this case well)
Vertical schedule support
Better login cacheing
Darkmode (I tried this but it was so plain it seemed pointless)
Upload to github