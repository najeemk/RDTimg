from imagine_dl import Imagine
from PIL import Image
import os

os.system('clear')
print("*" * 35 + "\n* Imagine Reddit Image Downloader *\n" + "*" * 35 + "\n")

download = Imagine("config.json")
download.createSubredditInstance()
download.generateSubmissionIter()

while True:
    img = download.imageSelection()
    if not(img is None):
        img = Image.open(img)
        img.show()
        option = input("Save (s), next (n), quit (q): ")
        download.imageOption(option)