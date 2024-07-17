from flask import Flask, request, render_template, send_from_directory, jsonify, send_file
from flask_socketio import SocketIO, emit
from css_factor import tokenize, Parser, factor_css, explode_css, render_stylesheet
from tqdm import tqdm
import io
import traceback
import time
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
socketio = SocketIO(app, async_mode='threading')

class TqdmToLogger:
    def __init__(self, logger):
        self.logger = logger
        self.last_message = ''

    def write(self, buf):
        message = buf.strip()
        if message and message != self.last_message:
            self.logger(message)
            self.last_message = message

    def flush(self):
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/process', methods=['POST'])
def process_css():
    logs = []
    if 'cssFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['cssFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    mode = request.form.get('mode', 'factor')
    css_input = file.read().decode('utf-8')

    socketio.emit('log', {'message': f"Processing CSS in {mode} mode"})


    try:
        socketio.emit('log', {'message': "Tokenizing CSS"})
        tokens = list(tokenize(css_input, progress_callback=lambda p: socketio.emit('progress', {'task': 'Tokenizing', 'progress': p})))
        socketio.emit('log', {'message': f"Generated {len(tokens)} tokens"})

        socketio.emit('log', {'message': "Parsing CSS"})
        css_parser = Parser(tokens)
        css_parser.set_progress_callback(lambda p: socketio.emit('progress', {'task': 'Parsing', 'progress': p / len(tokens) * 100}))
        stylesheet = css_parser.parse()

        if css_parser.errors:
            for error in css_parser.errors:
                socketio.emit('log', {'message': f"Parsing error: {error}"})

        if not stylesheet.statements:
            socketio.emit('log', {'message': "Warning: No valid CSS statements were parsed"})
        else:
            socketio.emit('log', {'message': f"CSS parsed successfully. Found {len(stylesheet.statements)} statements."})

        if mode == 'factor':
            socketio.emit('log', {'message': "Factoring CSS"})
            processed_stylesheet = factor_css(stylesheet, lambda p: socketio.emit('progress', {'task': 'Factoring', 'progress': p}))
        elif mode == 'explode':
            socketio.emit('log', {'message': "Exploding CSS"})
            processed_stylesheet = explode_css(stylesheet, lambda p: socketio.emit('progress', {'task': 'Exploding', 'progress': p}))
        else:  # identity
            socketio.emit('log', {'message': "Processing CSS in identity mode"})
            processed_stylesheet = stylesheet

        socketio.emit('log', {'message': "Rendering processed stylesheet"})
        result = render_stylesheet(processed_stylesheet)
        socketio.emit('log', {'message': f"Rendered stylesheet length: {len(result)} characters"})

        output_filename = f"processed_{mode}_{int(time.time())}.css"
        output_path = os.path.join('static', 'output', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result)
        socketio.emit('log', {'message': f"Saved processed CSS to {output_filename}"})

        socketio.emit('log', {'message': "Processing complete"})

        return jsonify({'result': result, 'filename': output_filename}), 200
    except Exception as e:
        error_message = f"Error processing CSS: {str(e)}"
        socketio.emit('log', {'message': error_message})
        socketio.emit('log', {'message': traceback.format_exc()})
        return jsonify({'error': error_message}), 500


def log(message):
    logs.append(message)
    print(message)  # Print to terminal
    socketio.emit('log', {'message': message})  # Send to frontend

    tqdm_out = TqdmToLogger(log)

    if 'cssFile' not in request.files:
        return jsonify({'error': 'No file part', 'logs': logs}), 400
    file = request.files['cssFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file', 'logs': logs}), 400

    mode = request.form.get('mode', 'factor')
    css_input = file.read().decode('utf-8')

    log(f"Processing CSS in {mode} mode")

    try:
        log("Tokenizing CSS")
        tokens = []
        for _ in tqdm(tokenize(css_input), desc="Tokenizing", file=tqdm_out, unit=" tokens"):
            tokens.append(_)
            time.sleep(0.01)  # Artificial delay for demonstration
            socketio.emit('progress', {'task': 'Tokenizing', 'progress': len(tokens) / len(css_input) * 100})
        log(f"Generated {len(tokens)} tokens")

        log("Parsing CSS")
        css_parser = Parser(tokens)
        with tqdm(total=len(tokens), desc="Parsing", file=tqdm_out, unit=" tokens") as pbar:
            def update_progress(progress):
                pbar.update(progress - pbar.n)
                socketio.emit('progress', {'task': 'Parsing', 'progress': progress / len(tokens) * 100})
            css_parser.set_progress_callback(update_progress)
            stylesheet = css_parser.parse()

        if css_parser.errors:
            for error in css_parser.errors:
                log(f"Parsing error: {error}")

        if not stylesheet.statements:
            log("Warning: No valid CSS statements were parsed")
        else:
            log(f"CSS parsed successfully. Found {len(stylesheet.statements)} statements.")

        if mode == 'factor':
            log("Factoring CSS")
            with tqdm(total=100, desc="Factoring", file=tqdm_out, unit="%") as pbar:
                def factor_progress(progress):
                    pbar.update(progress - pbar.n)
                    socketio.emit('progress', {'task': 'Factoring', 'progress': progress})
                processed_stylesheet = factor_css(stylesheet, factor_progress)
        elif mode == 'explode':
            log("Exploding CSS")
            with tqdm(total=100, desc="Exploding", file=tqdm_out, unit="%") as pbar:
                def explode_progress(progress):
                    pbar.update(progress - pbar.n)
                    socketio.emit('progress', {'task': 'Exploding', 'progress': progress})
                processed_stylesheet = explode_css(stylesheet, explode_progress)
        else:  # identity
            log("Processing CSS in identity mode")
            processed_stylesheet = stylesheet

        log("Rendering processed stylesheet")
        result = render_stylesheet(processed_stylesheet)
        log(f"Rendered stylesheet length: {len(result)} characters")

        # Save the result to a file
        output_filename = f"processed_{mode}_{int(time.time())}.css"
        output_path = os.path.join('static', 'output', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result)
        log(f"Saved processed CSS to {output_filename}")

        log("Processing complete")

        return jsonify({
            'result': result,
            'logs': logs,
            'filename': output_filename
        }), 200
    except Exception as e:
        error_message = f"Error processing CSS: {str(e)}"
        log(error_message)
        log(traceback.format_exc())
        return jsonify({
            'error': error_message,
            'logs': logs
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join('static', 'output', filename), as_attachment=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)