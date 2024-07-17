const form = document.getElementById('cssForm');
const resultDiv = document.getElementById('result');
const downloadLink = document.getElementById('downloadLink');

// Apply syntax highlighting to code blocks
document.querySelectorAll('pre code').forEach((block) => {
    if (block.className === 'language-css') {
        Prism.highlightElement(block);
    }
});

form.addEventListener('submit', async(e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.textContent = data.result;
            downloadLink.href = `/download/${data.filename}`;
            downloadLink.style.display = 'inline-block';
        } else {
            resultDiv.textContent = data.error || 'An error occurred while processing the CSS.';
            downloadLink.style.display = 'none';
        }
    } catch (error) {
        resultDiv.textContent = 'An error occurred while sending the request.';
        downloadLink.style.display = 'none';
    }
});