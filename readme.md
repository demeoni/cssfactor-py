Converted of This Project
Original is Java code:
http://zamez.org/source/factorcss/
http://zamez.org/factorcss
by James Bursa - https://github.com/jamesbursa

Converted to Pyhton by demeoni,
Thank to Claude 3.5 Sonnet

Aim of the project is, delete duplicates from CSS file to make it better. Many people used it for merge 2 css files into 1 css.

I hope it will work in Py too.

# 17.07.2024 #

# Backend
* Added tqdm, (tqdm is a fast, extensible progress bar for Python and CLI) will provide a visual progress indicator for the CSS processing steps.
* Added a consume whitespace method to skip over unexpected whitespace.
* Added error handling in frontend and a synchronize method to recover from parsing errors.

# Frontend
* Console View in HTML for errors.