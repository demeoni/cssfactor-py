# CssFactor (Python)
## Aim of the project
Aim of the project is, delete duplicates, merge classes in CSS file to make it better reading for dev team. Many people used it for merge 2 css files into 1 css. First you have to merge (copy/paste) manually in 1 css file first. Than upload here to let the magic work.

## Credits
Python by [demeoni](https://github.com/demeoni)
Thanks to "Claude 3.5 Sonnet" by Anthropic

## Project Inspire
Tried to Convert of This Project
Original code is in Java:
http://zamez.org/source/factorcss/ - http://zamez.org/factorcss
by [James Bursa](https://github.com/jamesbursa)

I hope it will work in Py too.

### No, its not fully converted
nope.. it won't worked fully..

Actually It's not Fully 1-1 Converted Project.
It's kind a inspired project now.
At least I've tried it.

### How it Works?
1. Manually add (copy/paste) all css code-lines into one single .css file,
2. Select your function on page (Factor, Explode, Identity), Read [Guide.md](./static/guide.md)
3. Upload your File,
4. Checkmark for Remove Leftover brackets.
5. Click "Process" button.
6. View Edits in Preview Panel
7. You can re-select your function again after upload and process of file.
8. Download File button is after the CSS code panel. Scroll down for it.


### Updates
### 17.07.2024 - evening

* Added option to remove leftover { , [ ,  ] , }
* Output file succesful,
* Removed tqdm. Will Add later,
* Simplified Python code,


### 17.07.2024 - morning

* Output not succesful. Zero bytes files.
* Parsing have problems.

### Backend
* Added tqdm for Frontend Console view,
* Added tqdm for Backend Terminal view, (tqdm is a fast, extensible progress bar for Python and CLI) will provide a visual progress indicator for the CSS processing steps,
* Added a consume whitespace method to skip over unexpected whitespace.
* Added error handling in frontend and a synchronize method to recover from parsing errors.
* Converted from Java to Py.

### Frontend
* Console View in HTML for errors.
* Guide Added for Functions.
