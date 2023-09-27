from py3270 import Emulator
import sys, os

host = "155.210.152.51"
port = 3270
e = Emulator(visible=True)
e.connect('155.210.152.51:3270')
e.terminate()