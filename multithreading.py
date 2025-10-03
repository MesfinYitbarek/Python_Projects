#multithreading

import threading
import time

def walk_dog(first, last):
    time.sleep(8)
    print(f"you finish walking")
def take_out_trash():
    time.sleep(2)
    print(f"you take out the trash")
def get_email():
    time.sleep(4)
    print(f"you get the email")  

chore1 = threading.Thread(target=walk_dog, args=("Scooby", "Doo"))
chore1.start()
chore2 = threading.Thread(target=take_out_trash)
chore2.start()
chore3 = threading.Thread(target=get_email,)
chore3.start()