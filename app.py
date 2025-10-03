import random
import math
course = "Python Programming"
course_ex = "Python \"programming"
course_exe = "Python \\programming"
course_exf = "Python \nprogramming"
print(len(course))
print(course[0])
print(course[-1])
print(course[0:3])
print(course[:])
print(course[:3])
print(course[0:])
print(course_ex)
print(course_exe)
print(course_exf)
print(course.upper())
print(course.capitalize())
print(course.title())
print(course.find("Pro"))
print(course.replace("P", "j"))
print("Pro" in course)
print("Pro" not in course)
first = "Python"
last = "programming"
full = first + " " + last
fullf = f"{last} {first}"
print(full)
print(fullf)

print(10 + 3)
print(10 / 3)
print(10 // 3)  # round
print(10 ** 3)  # exponent
print(10 % 3)  # modules

print(round(3.3))
print(abs(-2.9))

print(math.ceil(2.2))

x = input("x:")
y = int(x) + 1
print(f"x:{x} y:{y}")

# int
# bool
# str
# float

# conditional statements
temperature = 35
if temperature > 30:
    print("it's hot")
elif temperature > 20:
    print("it's not that much hot")
else:
    print("it's cold")
print("Done")

# ternary operator
age = 30
message = "eligible" if age >= 18 else "not eligible"
print(message)
# logical operator
high_income = True
good_credit = True
student = True

if high_income and good_credit:  # and,or,not
    print("eligible")
else:
    print("not eligible")

# chaining comparison
if age >= 12 and age < 18:
    print("eligible")

if 12 >= age < 18:  # same as above
    print("eligible")

# for loop
for number in range(3):
    print("Attempt", number + 1, (number + 1) * ".")
for number in range(1, 4):
    print("Attempt", number, (number) * ".")
for number in range(1, 10, 2):
    print("Attempt", number, (number) * ".")

successful = True
for number in range(3):
    print("Attempt")
    if successful:
        print("successful")
        break
else:
    print("not successful")
# nested loop

for x in range(5):
    for y in range(3):
        print(f"{x}, {y}")
# iterable

for x in "Python":
    print(x)
for x in [1, 2, 3, 4]:
    print(x)
# while loop

command = ""
while command.lower() != "quite":
    command = input(">")
    print("ECHO", command)

count = 0
for number in range(2, 10, 2):
    count += 1
    print(number)
print(f"we have {count} even")


def multiply(*numbers):
    total = 1
    for number in numbers:
        total *= number
    return total


print(multiply(2, 3, 4, 5))

# List = [] ordered and changeable. Duplicates are ok
# set = {} unordered and immutable, but Add/Remove Ok. No Duplicate
# Tuple = () ordered and unchangeable, Duplicates are ok, faster
fruits = ["apple", "orange", "banana"]
fruits.append("pineapple")
fruits.remove("apple")
fruits.insert(0, "pineapple")
fruits.sort()
fruits.reverse()
fruits.clear()
fruits.index("apple")
fruits.count("pineapple")
print(fruits)

# dictionaries
# key value pare

num = random.randint(1, 10) #int
num = random.random(1, 10) #float
print(num)
cards = ["2","3","4","g"]
random.shuffle(cards)
options = ("rock", "paper", "scissors")
option = random.choice(options)
print(option)


#default arguments
#keyword arguments
#list comprehension
grades = [85,23,23,45,67]
passing_grades = [grade for grade in grades if grade >= 60]
print(passing_grades)

#switch

def day_of_weeks(day):
    if day == 1:
        return "it is sunday"
    elif day == 2:
        return "it is tuesday"
    else:
        return "not a valid day"
print(day_of_weeks(1))
#match-case switch
def day_of_weeks(day):
    match day:
        case 1:
            return "it is sunday"
        case 2:
            return "it is tuesday"
        case _:
            return "not a valid day"
print(day_of_weeks(1))


#modules
#import math
#import math as m
#from math import pi
#print(help("modules"))
#scope resolution  = Local, Enclosed, Global and Built in

class Car:
    def __init__(self, model, year, for_sale):
        self.model = model
        self.year = year
        self.for_sale = for_sale
car1 = Car("Musting", 2024, "red", False)
print(car1.model)
print(car1.year)

#inheritance
class Animal:
    def __init__(self, name):
        self.name = name
        self.is_alive = True
    
    def eat(self):
        print(f"{self.name} is eating")
    def sleep(self):
        print(f"{self.name} is asleep")
class Dog(Animal):
    pass
class Cat(Animal):
    pass

dog = Dog("dog")
cat = Cat("Garfield")

print(dog.name)


#multiple inheritance and multilevel inheritance

class Animal:
    def __init__(self, name):
        self.name = name
    def eat(self):
        print("This animal is eating")
    def sleep(self):
        print("This animal is sleeping")
class Prey(Animal):
    def flee(self):
        print("this animal is fleeing")

class Predator(Animal):
    def hunt(self):
        print("This animal is hunting")
class Hawk(Predator):
    pass
class Fish(Prey, Predator):
    pass

hawk = Hawk()
fish = Fish()

fish.eat()

#super() = function in a child class to call methods from a parent class. Allows to extend the functionality of the inherited methods.

class Shape:
    def __init__(self, color, is_filled):
        self.color = color
        self.is_filled = is_filled
    def describe(self):
        print(f"It is {self.color} and { 'filled' if self.is_filled else 'not filled'}" )
class Square:
    def __init__(self, color, is_filled, width):
        super().__init__(color, is_filled)
        self.width = width
    def describe(self):
        super().describe()
class Circle(Shape):
    def __init__(self, color, is_filled, radius):
        super().__init__(color, is_filled)
        self.radius = radius
    def describe(self):
        print(f"It is a circle with an area of {3.14 * self.radius * self.radius}cm^2")
        super().describe()
class Triangle:
    def __init__(self, color, is_filled, width):
        super().__init__(color, is_filled)
        self.width = width
    def describe(self):
        super().describe()

circle = Circle(color="red", is_filled=True, radius=5)
square = Square(color="blue", is_filled=True, width=6)

circle.describe()

#static and instance methods

class Employee:
    def __init__(self, name, position):
        self.name = name
        self.position = position
    def get_info(self):
        return f"{self.name} = {self.position}"
    @staticmethod
    def is_valid_position(position):
        valid_positions = ["Manager", "Casher"]
        return position in valid_positions
    
Employee.is_valid_position("Manger")  #static.. best for utility functions that do not need access to class data
employee = Employee("Eugene", "manager") #instance

#magic methods
class Book:
    def __init__(self):
        pass
    def __str__(self):
        pass
    def __eq__(self, value):
        pass
    def __add__(self, value):
        pass
    def __getitem__(self, key):
        pass
# python file detection

import os

file_path = "test.txt"

if os.path.exists(file_path): #os.path.isfile(file_path), os.path.isdir(file_path)
    print(f"Location: {file_path}")
else:
    print("Location not found")

#writing files
#.text
text_data = "I like chicken"
file_path = "output.txt"
with open(file_path, "w") as file: #w - override the file..x - create new file, a --append 
    file.write(text_data)
    print(f"text file '{file_path}' was created")

#json
import json
employee = {
    "name": "mepa",
    "age": 23,
    "job": "cook"
}

file_path = "output.json"
try:
    with open(file_path, "w") as file:
        json.dump(employee, file, indent=4)
        print(f"json file '{file_path}' was created")
except FileExistsError:
    print("This file already exists")

#csv
import csv
employee = [ ["name", age, "job"],
             ["mepa", 23, "SoftEng"]
            ["kira", 24, "SoftEng"]]

file_path = "output.json"
try:
    with open(file_path, "w") as file:
        writer = csv.writer( file)
        for row in employee:
            writer.writerow()
        print(f"csv file '{file_path}' was created")
except FileExistsError:
    print("This file already exists")

#reading files
#.txt
file_path = "output.txt"
with open(file_path, "r") as file: #w - override the file..x - create new file, a --append 
    content = file.read()
    print(content)

#json
file_path = "output.txt"
with open(file_path, "r") as file: 
    content = json.load(file)
    print(content)
#csv
file_path = "output.txt"
with open(file_path, "r") as file: 
    content = csv.reader(file)
    for line in content:
        print(line)

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

#how to connect to an api using python

import requests
base_url = "https://pokeapi.co/api/v2/"

def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")

pokemon_name = "typhlosion"
pokemon_info = get_pokemon_info(pokemon_name)

if pokemon_info:
    print(f"Name: {pokemon_info["name"].capitalize()}")
    print(f"Id: {pokemon_info["id"]}")