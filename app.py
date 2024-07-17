# File: app.py

from flask import Flask, request, render_template, jsonify, send_file
from css_factor import process_css
import os
import time
import markdown
import re

app = Flask(__name__)

def custom_css_formatter(source):
    return f'<pre><code class="language-css">{source}</code></pre>'

def format_css_blocks(md):
    pattern = re.compile(r'```css\n(.*?)\n```', re.DOTALL)
    return pattern.sub(lambda m: custom_css_formatter(m.group(1)), md)

@app.route('/')
def index():
    with open('static/guide.md', 'r') as f:
        guide_content = f.read()
    formatted_guide = format_css_blocks(guide_content)
    guide_html = markdown.markdown(formatted_guide)
    return render_template('index.html', guide=guide_html)

@app.route('/process', methods=['POST'])
def process():
    if 'cssFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['cssFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    mode = request.form.get('mode', 'factor')
    css_input = file.read().decode('utf-8')

    try:
        result = process_css(css_input, mode)

        # Save the result to a file
        output_filename = f"processed_{mode}_{int(time.time())}.css"
        output_path = os.path.join('static', 'output', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result)

        return jsonify({'result': result, 'filename': output_filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join('static', 'output', filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)