import os
import shlex
import signal
import subprocess
import time

# cmd = 'go run ../remoteScheTest/*.go --config=../remoteScheTest/config'
# args = shlex.split(cmd)

child = subprocess.Popen('go run ../remoteScheTest/*.go --config=../remoteScheTest/config', shell=True, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Tester pid: ", end = '')
print(child.pid)

print("Tester code: ", end = '')
print(child.poll())

for i in range(10):
    print(i)
    time.sleep(1)

print("Kill tester")
os.killpg(child.pid, signal.SIGTERM)
# child.terminate()

child.wait()

print("Tester code: ", end = '')

print(child.poll())