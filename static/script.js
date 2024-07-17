const form = document.getElementById('cssForm');
const resultDiv = document.getElementById('result');
const downloadLink = document.getElementById('downloadLink');
const guideDiv = document.getElementById('guide');
const consoleDiv = document.getElementById('console');
const progressContainer = document.getElementById('progressContainer');
const progressTask = document.getElementById('progressTask');
const progressBarFill = document.querySelector('.progress-bar-fill');

const socket = io();

socket.on('log', function(data) {
    logToConsole(data.message);
});

socket.on('progress', function(data) {
    progressContainer.style.display = 'block';
    progressTask.textContent = data.task;
    progressBarFill.style.width = `${data.progress}%`;
});

function logToConsole(message, type = 'info') {
    const logElement = document.createElement('div');
    logElement.classList.add(`console-${type}`);
    logElement.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    consoleDiv.appendChild(logElement);
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

form.addEventListener('submit', async(e) => {
    e.preventDefault();
    const formData = new FormData(form);

    consoleDiv.innerHTML = ''; // Clear previous logs
    progressContainer.style.display = 'none';
    progressBarFill.style.width = '0%';

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.textContent = data.result;
            resultDiv.classList.remove('error');
            if (data.filename) {
                downloadLink.href = `/download/${data.filename}`;
                downloadLink.style.display = 'inline-block';
            }
        } else {
            resultDiv.textContent = data.error || 'An error occurred while processing the CSS.';
            resultDiv.classList.add('error');
            downloadLink.style.display = 'none';
        }

        // Log all messages
        data.logs.forEach(log => logToConsole(log));
    } catch (error) {
        resultDiv.textContent = 'An error occurred while sending the request.';
        resultDiv.classList.add('error');
        downloadLink.style.display = 'none';
        logToConsole('Error sending request: ' + error.message, 'error');
    }
});

// Load and render the guide
fetch('/static/guide.md')
    .then(response => response.text())
    .then(text => {
        guideDiv.innerHTML = marked.parse(text);
    })
    .catch(error => {
        logToConsole('Error loading guide: ' + error.message, 'error');
    });