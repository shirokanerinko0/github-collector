import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))



from src.visualization.dashboard import run_command_realtime
output, return_code = run_command_realtime("python main.py")
print(output)
print(return_code)
