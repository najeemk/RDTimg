from imagine_dl import Imagine
import os

os.system('clear')
print("*" * 35 + "\n* Imagine Reddit Image Downloader *\n" + "*" * 35 + "\n")

download = Imagine("config.json")
download.subredditInstance()
download.imageCycle()