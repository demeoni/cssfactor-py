# CssFactor (Python)
Converted of This Project
Original code is in Java:
http://zamez.org/source/factorcss/ - http://zamez.org/factorcss
by [James Bursa](https://github.com/jamesbursa)

Converted to Python by [demeoni](https://github.com/demeoni)
Thanks to "Claude 3.5 Sonnet" by Anthropic

## Aim of the project
Aim of the project is, delete duplicates from CSS file to make it better reading for dev team. Many people used it for merge 2 css files into 1 css. First you have to merge manually in 1 css first. Than upload here to let the magic work.

I hope it will work in Py too.
nope.. it won't worked fully..

Actually It's not Fully 1-1 Converted Project. It's kind a inspired project now. At least I've tried it.

### How it Works?
1. Manually add (copy/paste) all css code-lines into one single .css file,
2. Select your function on page (Factor, Explode, Identity), Read [Guide.md](./static/guide.md)
3. Upload your File,
4. Click "Process" button.


### Updates
### 17.07.2024 - evening

* Output file succesful.
* Removed tqdm. Will Add later.
* Simplified py



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
