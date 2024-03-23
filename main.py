from flask import Flask, request
import subprocess
import signal
import os

app = Flask(__name__)

process = None #GLOBAL VAR

@app.route("/<script_name>/<action>", methods=['GET'])
def manage_script(script_name, action):
    global process

    # Check if right actions
    if action not in ['start', 'stop', 'help']:
        return "Invalid action"
    
    # Run or stop script
    if action == 'start':
        args = [f'--{key}={value}' for key, value in request.args.items()]
        script_path = f'scripts/{script_name}.py'
        process = subprocess.Popen(['sudo', '-E', 'python3', script_path] + args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return f'Script {script_name} started with arguments: {args}'
    elif action == 'stop':
        if process is not None and process.poll() is None:
            process.kill()
            process = None
            return f'Script {script_name} stopped.'
    elif action == 'help':
        script_path = f'scripts/{script_name}.py'
        result = subprocess.run(['python3', script_path, '--help'], capture_output=True, text=True)
        return result.stdout
    else:
        return f'No script {script_name} runnning.'

if __name__ == "__main__":
    app.run(debug=True)