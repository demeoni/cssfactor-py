from flask import Flask, request, send_file, render_template, send_from_directory
from css_factor import tokenize, Parser, factor_css, explode_css, render_stylesheet
import io

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/process', methods=['POST'])
def process_css():
    if 'cssFile' not in request.files:
        return 'No file part', 400
    file = request.files['cssFile']
    if file.filename == '':
        return 'No selected file', 400

    mode = request.form.get('mode', 'factor')
    css_input = file.read().decode('utf-8')

    tokens = list(tokenize(css_input))
    css_parser = Parser(tokens)
    stylesheet = css_parser.parse()

    if mode == 'factor':
        processed_stylesheet = factor_css(stylesheet)
    elif mode == 'explode':
        processed_stylesheet = explode_css(stylesheet)
    else:  # identity
        processed_stylesheet = stylesheet

    return render_stylesheet(processed_stylesheet)

if __name__ == "__main__":
    app.run(debug=True)