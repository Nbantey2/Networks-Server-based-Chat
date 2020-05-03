import threading
import time

def output_stuff():
    while True:
        print('boing')
        time.sleep(2)

threading.Thread(target=output_stuff).start()

q = False
while not(q):
    inputtext = input('> ')
    print(inputtext)