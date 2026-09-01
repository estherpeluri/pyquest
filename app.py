from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import tempfile
import sqlite3
from datetime import date, datetime


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)
app.secret_key = "pyquest_secret_key_2026"

DATABASE = "pyquest.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CHECK IF COLUMN EXISTS
# ============================================================

def column_exists(connection, table_name, column_name):

    columns = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        column["name"] == column_name
        for column in columns
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    connection = get_db()
    cursor = connection.cursor()


    # ========================================================
    # USERS TABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            current_level INTEGER DEFAULT 1,

            completed_levels INTEGER DEFAULT 0,

            streak INTEGER DEFAULT 0,

            certificates INTEGER DEFAULT 0,

            xp INTEGER DEFAULT 0,

            last_active TEXT DEFAULT '',

            assessment_score INTEGER DEFAULT 0,

            skill_level TEXT DEFAULT ''

        )
    """)


    # ========================================================
    # SAFE DATABASE UPGRADES
    # ========================================================

    if not column_exists(connection, "users", "xp"):

        cursor.execute(
            "ALTER TABLE users "
            "ADD COLUMN xp INTEGER DEFAULT 0"
        )


    if not column_exists(connection, "users", "last_active"):

        cursor.execute(
            "ALTER TABLE users "
            "ADD COLUMN last_active TEXT DEFAULT ''"
        )


    if not column_exists(connection, "users", "assessment_score"):

        cursor.execute(
            "ALTER TABLE users "
            "ADD COLUMN assessment_score INTEGER DEFAULT 0"
        )


    if not column_exists(connection, "users", "skill_level"):

        cursor.execute(
            "ALTER TABLE users "
            "ADD COLUMN skill_level TEXT DEFAULT ''"
        )


    # ========================================================
    # PROGRESS TABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            level INTEGER NOT NULL,

            completed INTEGER DEFAULT 0,

            FOREIGN KEY(user_id)
            REFERENCES users(id)

        )
    """)


    connection.commit()
    connection.close()


# ============================================================
# ASSESSMENT ANSWERS
# ============================================================

assessment_answers = {

    "q1": "print",
    "q2": "=",
    "q3": "8",
    "q4": "input",
    "q5": "%",
    "q6": "if",
    "q7": "int",
    "q8": "memoization",
    "q9": "list",
    "q10": "def",

    "q11": "length",
    "q12": "for",
    "q13": "0-4",
    "q14": "break",
    "q15": "continue",
    "q16": "dict",
    "q17": "set",
    "q18": "o1",
    "q19": "try",
    "q20": "self",

    "q21": "stop",
    "q22": "binary",
    "q23": "logn",
    "q24": "kadane",
    "q25": "divide",
    "q26": "stack",
    "q27": "queue",
    "q28": "bfs",
    "q29": "subproblems",
    "q30": "performance"

}

# ============================================================
# PYQUEST LEVEL DATA
# ============================================================

levels = {

    # ========================================================
    # WORLD 1 — PYTHON BEGINNINGS
    # ========================================================

    1: {
        "title": "Hello, Python!",
        "world": "Python Beginnings",
        "difficulty": "Easy",
        "concept": "print()",
        "question": "Write a Python program that prints Hello, Python!",
        "starter_code": "# Write your code below\n",
        "expected": "print",
        "hint": "Python displays text using the print() function.",
        "help": "Example: print('Hello, Python!')",
        "pseudo": "START → Print 'Hello, Python!' → END",
        "explanation": "The print() function is used to display information on the screen."
    },

    2: {
        "title": "Meet the Variables",
        "world": "Python Beginnings",
        "difficulty": "Easy",
        "concept": "Variables",
        "question": "Create a variable called name and store your name in it.",
        "starter_code": "# Create a variable called name\n",
        "expected": "name",
        "hint": "A variable stores information.",
        "help": "Example: name = 'Esther'",
        "pseudo": "START → Create variable → Store a name → END",
        "explanation": "Variables allow us to store values so we can use them later."
    },

    3: {
        "title": "Number Power",
        "world": "Python Beginnings",
        "difficulty": "Easy",
        "concept": "Numbers and Addition",
        "question": "Create two numbers and print their sum.",
        "starter_code": "# Create two numbers\n# Print their sum\n",
        "expected": "+",
        "hint": "Use the + operator to add numbers.",
        "help": "Example: a = 10, b = 20, then print(a + b)",
        "pseudo": "START → Create A → Create B → Add A + B → Print result → END",
        "explanation": "Python supports arithmetic operations such as addition, subtraction, multiplication and division."
    },

    4: {
        "title": "Your First Input",
        "world": "Python Beginnings",
        "difficulty": "Easy",
        "concept": "input()",
        "question": "Ask the user for their name and print it.",
        "starter_code": "# Ask the user for their name\n",
        "expected": "input",
        "hint": "Use input() to receive information from the user.",
        "help": "Store input() in a variable and then print the variable.",
        "pseudo": "START → Ask for name → Store name → Print name → END",
        "explanation": "The input() function allows a Python program to receive information from the user."
    },

    5: {
        "title": "Even or Odd",
        "world": "Python Beginnings",
        "difficulty": "Easy",
        "concept": "if / else",
        "question": "Write a program to check whether a number is even or odd.",
        "starter_code": "# Check whether a number is even or odd\n",
        "expected": "if",
        "hint": "Use the modulo operator %.",
        "help": "If number % 2 == 0, print Even. Otherwise print Odd.",
        "pseudo": "START → Get number → Check number % 2 → If 0 → Even → Else → Odd → END",
        "explanation": "Conditional statements allow programs to make decisions based on conditions."
    },


    # ========================================================
    # WORLD 2 — LOOP VALLEY
    # ========================================================

    6: {
        "title": "Count With Python",
        "world": "Loop Valley",
        "difficulty": "Easy",
        "concept": "for loop",
        "question": "Print numbers from 1 to 5 using a for loop.",
        "starter_code": "# Print numbers from 1 to 5\n",
        "expected": "for",
        "hint": "A for loop repeats instructions.",
        "help": "Try using: for i in range(1, 6):",
        "pseudo": "START → Repeat from 1 to 5 → Print number → END",
        "explanation": "A for loop repeats a block of code for a sequence of values."
    },

    7: {
        "title": "Sum It Up",
        "world": "Loop Valley",
        "difficulty": "Easy",
        "concept": "Loop and Accumulator",
        "question": "Find the sum of numbers from 1 to 10 using a loop.",
        "starter_code": "# Find the sum from 1 to 10\n",
        "expected": "for",
        "hint": "Create a variable to store the running total.",
        "help": "Start total = 0 and add each number inside the loop.",
        "pseudo": "START → total = 0 → Loop 1 to 10 → Add number → Print total → END",
        "explanation": "An accumulator is a variable that stores a continuously changing value."
    },

    8: {
        "title": "While You Wait",
        "world": "Loop Valley",
        "difficulty": "Easy",
        "concept": "while loop",
        "question": "Print numbers from 1 to 5 using a while loop.",
        "starter_code": "# Print numbers using a while loop\n",
        "expected": "while",
        "hint": "A while loop continues while a condition is true.",
        "help": "Start with i = 1 and increase i inside the loop.",
        "pseudo": "START → i = 1 → While i <= 5 → Print i → Increase i → END",
        "explanation": "A while loop repeatedly executes code as long as its condition remains true."
    },

    9: {
        "title": "Table Master",
        "world": "Loop Valley",
        "difficulty": "Easy",
        "concept": "Multiplication Table",
        "question": "Print the multiplication table of 5 from 1 to 10.",
        "starter_code": "# Print the multiplication table of 5\n",
        "expected": "for",
        "hint": "Use a loop from 1 to 10.",
        "help": "Print 5 * i inside the loop.",
        "pseudo": "START → Loop 1 to 10 → Multiply 5 × i → Print result → END",
        "explanation": "Loops can be combined with arithmetic operations to solve repetitive problems."
    },

    10: {
        "title": "Pattern Starter",
        "world": "Loop Valley",
        "difficulty": "Easy",
        "concept": "Nested Loops",
        "question": "Print a square pattern of stars using nested loops.",
        "starter_code": "# Print a star pattern\n",
        "expected": "for",
        "hint": "One loop controls rows and another loop controls columns.",
        "help": "Use a for loop inside another for loop.",
        "pseudo": "START → Loop rows → Loop columns → Print stars → END",
        "explanation": "Nested loops are loops placed inside other loops and are useful for patterns."
    },


    # ========================================================
    # WORLD 3 — STRING STREET
    # ========================================================

    11: {
        "title": "String Explorer",
        "world": "String Street",
        "difficulty": "Easy",
        "concept": "Strings",
        "question": "Create a string called message and print it.",
        "starter_code": "# Create and print a string\n",
        "expected": "message",
        "hint": "Strings are written inside quotation marks.",
        "help": "Example: message = 'Hello Python'",
        "pseudo": "START → Create string → Store text → Print string → END",
        "explanation": "Strings are sequences of characters used to store text."
    },

    12: {
        "title": "Length Detective",
        "world": "String Street",
        "difficulty": "Easy",
        "concept": "len()",
        "question": "Create a string and print its length.",
        "starter_code": "# Find the length of a string\n",
        "expected": "len",
        "hint": "Python has a built-in function for length.",
        "help": "Use len(your_string).",
        "pseudo": "START → Create string → Find length → Print result → END",
        "explanation": "The len() function returns the number of characters in a string."
    },

    13: {
        "title": "First Character",
        "world": "String Street",
        "difficulty": "Easy",
        "concept": "String Indexing",
        "question": "Print the first character of a string.",
        "starter_code": "# Print the first character\n",
        "expected": "[0]",
        "hint": "Python indexing starts from 0.",
        "help": "Use string_name[0].",
        "pseudo": "START → Create string → Access index 0 → Print character → END",
        "explanation": "String indexing allows us to access individual characters."
    },

    14: {
        "title": "Reverse Explorer",
        "world": "String Street",
        "difficulty": "Medium",
        "concept": "String Slicing",
        "question": "Print a string in reverse order using slicing.",
        "starter_code": "# Reverse a string\n",
        "expected": "::-1",
        "hint": "Slicing can move backwards through a string.",
        "help": "Use string_name[::-1].",
        "pseudo": "START → Create string → Slice backwards → Print reversed string → END",
        "explanation": "Slicing allows us to extract or reverse parts of strings."
    },

    15: {
        "title": "Word Counter",
        "world": "String Street",
        "difficulty": "Medium",
        "concept": "String Methods",
        "question": "Count how many times the letter 'a' appears in a string.",
        "starter_code": "# Count the letter a\n",
        "expected": "count",
        "hint": "Strings have useful built-in methods.",
        "help": "Use string_name.count('a').",
        "pseudo": "START → Create string → Count 'a' → Print count → END",
        "explanation": "String methods allow us to perform useful operations on text."
    },


    # ========================================================
    # WORLD 4 — LIST LAND
    # ========================================================

    16: {
        "title": "List Builder",
        "world": "List Land",
        "difficulty": "Easy",
        "concept": "Lists",
        "question": "Create a list containing three numbers and print it.",
        "starter_code": "# Create your list\n",
        "expected": "[",
        "hint": "Lists use square brackets.",
        "help": "Example: numbers = [10, 20, 30]",
        "pseudo": "START → Create list → Store numbers → Print list → END",
        "explanation": "Lists allow us to store multiple values in one variable."
    },

    17: {
        "title": "List Explorer",
        "world": "List Land",
        "difficulty": "Easy",
        "concept": "List Indexing",
        "question": "Create a list and print its first element.",
        "starter_code": "# Access the first list element\n",
        "expected": "[0]",
        "hint": "List indexing starts from 0.",
        "help": "Use list_name[0].",
        "pseudo": "START → Create list → Access index 0 → Print element → END",
        "explanation": "List indexing allows us to access individual elements."
    },

    18: {
        "title": "Add More!",
        "world": "List Land",
        "difficulty": "Easy",
        "concept": "append()",
        "question": "Create a list and add a new element using append().",
        "starter_code": "# Add an item to a list\n",
        "expected": "append",
        "hint": "append() adds an element to the end of a list.",
        "help": "Example: numbers.append(40)",
        "pseudo": "START → Create list → Add item → Print list → END",
        "explanation": "The append() method adds a new element to the end of a list."
    },

    19: {
        "title": "Remove Mission",
        "world": "List Land",
        "difficulty": "Easy",
        "concept": "remove()",
        "question": "Create a list and remove one element from it.",
        "starter_code": "# Remove an item from a list\n",
        "expected": "remove",
        "hint": "Use the remove() method.",
        "help": "Example: numbers.remove(20)",
        "pseudo": "START → Create list → Remove item → Print list → END",
        "explanation": "The remove() method removes a specific value from a list."
    },

    20: {
        "title": "List Champion",
        "world": "List Land",
        "difficulty": "Medium",
        "concept": "List Loop",
        "question": "Create a list of numbers and print every element using a loop.",
        "starter_code": "# Print all list elements\n",
        "expected": "for",
        "hint": "Use a for loop to visit each list element.",
        "help": "Try: for item in numbers:",
        "pseudo": "START → Create list → Loop through list → Print each item → END",
        "explanation": "Loops are commonly used to process every element in a list."
    },


    # ========================================================
    # WORLD 5 — LOGIC KINGDOM
    # ========================================================

    21: {
        "title": "Positive or Negative",
        "world": "Logic Kingdom",
        "difficulty": "Easy",
        "concept": "Conditions",
        "question": "Write a program to check whether a number is positive or negative.",
        "starter_code": "# Check positive or negative\n",
        "expected": "if",
        "hint": "Compare the number with 0.",
        "help": "Use if number >= 0.",
        "pseudo": "START → Get number → Compare with 0 → Print result → END",
        "explanation": "Conditions allow programs to choose different actions."
    },

    22: {
        "title": "Age Gate",
        "world": "Logic Kingdom",
        "difficulty": "Easy",
        "concept": "if / else",
        "question": "Check whether a person is eligible to vote if age is 18 or above.",
        "starter_code": "# Check voting eligibility\n",
        "expected": "if",
        "hint": "Compare age with 18.",
        "help": "Use: if age >= 18:",
        "pseudo": "START → Get age → Compare with 18 → Eligible or Not Eligible → END",
        "explanation": "Comparison operators help programs make decisions."
    },

    23: {
        "title": "Logical Master",
        "world": "Logic Kingdom",
        "difficulty": "Medium",
        "concept": "Logical Operators",
        "question": "Check whether a number is between 10 and 50.",
        "starter_code": "# Check whether number is between 10 and 50\n",
        "expected": "and",
        "hint": "Two conditions can be joined together.",
        "help": "Use: number >= 10 and number <= 50",
        "pseudo": "START → Get number → Check >= 10 AND <= 50 → Print result → END",
        "explanation": "Logical operators such as and and or combine multiple conditions."
    },

    24: {
        "title": "Largest Number",
        "world": "Logic Kingdom",
        "difficulty": "Medium",
        "concept": "Multiple Conditions",
        "question": "Find the largest of two numbers using if and else.",
        "starter_code": "# Find the larger number\n",
        "expected": "if",
        "hint": "Compare the two numbers using >.",
        "help": "If a > b, print a. Otherwise print b.",
        "pseudo": "START → Get A and B → Compare → Print larger → END",
        "explanation": "Conditional logic can solve comparison problems."
    },

    25: {
        "title": "Logic Champion",
        "world": "Logic Kingdom",
        "difficulty": "Medium",
        "concept": "Nested Conditions",
        "question": "Check whether a number is positive, negative, or zero.",
        "starter_code": "# Check positive, negative or zero\n",
        "expected": "elif",
        "hint": "You need more than two possible outcomes.",
        "help": "Use if, elif and else.",
        "pseudo": "START → Get number → Check > 0 → Check < 0 → Otherwise zero → END",
        "explanation": "if, elif and else allow programs to handle multiple conditions."
    },


    # ========================================================
    # WORLD 6 — FUNCTION FOREST
    # ========================================================

    26: {
        "title": "Function First",
        "world": "Function Forest",
        "difficulty": "Easy",
        "concept": "Functions",
        "question": "Create a function called greet that prints Hello.",
        "starter_code": "# Create a function called greet\n",
        "expected": "def",
        "hint": "Functions are created using def.",
        "help": "Example: def greet():",
        "pseudo": "START → Define function → Print Hello → END",
        "explanation": "Functions allow us to organize reusable blocks of code."
    },

    27: {
        "title": "Call the Function",
        "world": "Function Forest",
        "difficulty": "Easy",
        "concept": "Function Call",
        "question": "Create a function called greet and call it.",
        "starter_code": "# Define and call greet\n",
        "expected": "greet()",
        "hint": "After defining a function, use its name with parentheses.",
        "help": "Call the function using greet().",
        "pseudo": "START → Define greet → Call greet → END",
        "explanation": "A function must be called for its code to execute."
    },

    28: {
        "title": "Parameter Power",
        "world": "Function Forest",
        "difficulty": "Medium",
        "concept": "Parameters",
        "question": "Create a function that accepts a name and prints it.",
        "starter_code": "# Create a function with a parameter\n",
        "expected": "def",
        "hint": "Parameters are written inside function parentheses.",
        "help": "Example: def greet(name):",
        "pseudo": "START → Define function → Accept name → Print name → END",
        "explanation": "Parameters allow functions to receive information."
    },

    29: {
        "title": "Return Mission",
        "world": "Function Forest",
        "difficulty": "Medium",
        "concept": "return",
        "question": "Create a function that returns the sum of two numbers.",
        "starter_code": "# Create a function that returns a sum\n",
        "expected": "return",
        "hint": "Use return to send a result back.",
        "help": "Inside the function use: return a + b",
        "pseudo": "START → Define function → Accept A and B → Return A + B → END",
        "explanation": "The return statement sends a value back from a function."
    },

    30: {
        "title": "Function Hero",
        "world": "Function Forest",
        "difficulty": "Medium",
        "concept": "Function Challenge",
        "question": "Create a function that checks whether a number is even.",
        "starter_code": "# Create an even checker function\n",
        "expected": "def",
        "hint": "Combine a function with the modulo operator.",
        "help": "Define a function, accept a number, then check number % 2.",
        "pseudo": "START → Define function → Accept number → Check modulo → Return or print result → END",
        "explanation": "Functions can combine logic into reusable solutions."
    },


    # ========================================================
    # WORLD 7 — COLLECTION CASTLE
    # ========================================================

    31: {
        "title": "Tuple Tower",
        "world": "Collection Castle",
        "difficulty": "Easy",
        "concept": "Tuples",
        "question": "Create a tuple containing three values.",
        "starter_code": "# Create a tuple\n",
        "expected": "(",
        "hint": "Tuples use parentheses.",
        "help": "Example: values = (1, 2, 3)",
        "pseudo": "START → Create tuple → Store values → Print tuple → END",
        "explanation": "Tuples store multiple values and are generally immutable."
    },

    32: {
        "title": "Set Quest",
        "world": "Collection Castle",
        "difficulty": "Easy",
        "concept": "Sets",
        "question": "Create a set containing three numbers.",
        "starter_code": "# Create a set\n",
        "expected": "{",
        "hint": "Sets use curly braces.",
        "help": "Example: numbers = {1, 2, 3}",
        "pseudo": "START → Create set → Store values → Print set → END",
        "explanation": "Sets store unique values."
    },

    33: {
        "title": "Dictionary Door",
        "world": "Collection Castle",
        "difficulty": "Medium",
        "concept": "Dictionaries",
        "question": "Create a dictionary with a name and age.",
        "starter_code": "# Create a dictionary\n",
        "expected": "{",
        "hint": "Dictionaries store key and value pairs.",
        "help": "Example: person = {'name': 'Alex', 'age': 20}",
        "pseudo": "START → Create dictionary → Add key-value pairs → Print dictionary → END",
        "explanation": "Dictionaries store data using keys and corresponding values."
    },

    34: {
        "title": "Dictionary Explorer",
        "world": "Collection Castle",
        "difficulty": "Medium",
        "concept": "Dictionary Access",
        "question": "Create a dictionary and print the value stored for the key name.",
        "starter_code": "# Access a dictionary value\n",
        "expected": "name",
        "hint": "Dictionary values are accessed using their keys.",
        "help": "Use dictionary_name['name'].",
        "pseudo": "START → Create dictionary → Access name key → Print value → END",
        "explanation": "Dictionary keys allow direct access to stored values."
    },

    35: {
        "title": "Collection Champion",
        "world": "Collection Castle",
        "difficulty": "Medium",
        "concept": "Collections",
        "question": "Create a dictionary and add a new key-value pair.",
        "starter_code": "# Add a new item to a dictionary\n",
        "expected": "=",
        "hint": "Assign a value to a new dictionary key.",
        "help": "Example: person['city'] = 'Vizag'",
        "pseudo": "START → Create dictionary → Add new key → Print dictionary → END",
        "explanation": "Collections can be modified and used to organize related data."
    },


    # ========================================================
    # WORLD 8 — CHALLENGE ARENA
    # ========================================================

    36: {
        "title": "Factor Finder",
        "world": "Challenge Arena",
        "difficulty": "Medium",
        "concept": "Number Logic",
        "question": "Print all factors of a number using a loop.",
        "starter_code": "# Find factors of a number\n",
        "expected": "for",
        "hint": "Check numbers that divide the given number without remainder.",
        "help": "Use if number % i == 0 inside a loop.",
        "pseudo": "START → Get number → Loop through possible divisors → Check remainder → Print factor → END",
        "explanation": "Loops and conditions can work together to solve number problems."
    },

    37: {
        "title": "Palindrome Quest",
        "world": "Challenge Arena",
        "difficulty": "Medium",
        "concept": "String Logic",
        "question": "Check whether a word is a palindrome.",
        "starter_code": "# Check palindrome\n",
        "expected": "::-1",
        "hint": "Compare the word with its reversed version.",
        "help": "Use word[::-1] to reverse a string.",
        "pseudo": "START → Get word → Reverse word → Compare → Print result → END",
        "explanation": "A palindrome reads the same forwards and backwards."
    },

    38: {
        "title": "List Maximum",
        "world": "Challenge Arena",
        "difficulty": "Medium",
        "concept": "List Problem",
        "question": "Find the largest number in a list.",
        "starter_code": "# Find the largest list element\n",
        "expected": "max",
        "hint": "Python provides a function to find the largest value.",
        "help": "Use max(numbers).",
        "pseudo": "START → Create list → Find maximum → Print result → END",
        "explanation": "Built-in functions can solve common collection problems."
    },

    39: {
        "title": "Star Challenge",
        "world": "Challenge Arena",
        "difficulty": "Medium",
        "concept": "Patterns",
        "question": "Print a triangle pattern using nested loops.",
        "starter_code": "# Print a triangle pattern\n",
        "expected": "for",
        "hint": "Use one loop for rows.",
        "help": "A simple pattern can be made with a loop and '*' * i.",
        "pseudo": "START → Loop rows → Create stars → Print row → END",
        "explanation": "Patterns improve understanding of loops and repeated logic."
    },

    40: {
        "title": "Arena Champion",
        "world": "Challenge Arena",
        "difficulty": "Hard",
        "concept": "Mixed Challenge",
        "question": "Find the sum of even numbers from 1 to 20.",
        "starter_code": "# Find sum of even numbers\n",
        "expected": "for",
        "hint": "Use a loop and check whether each number is even.",
        "help": "Use if i % 2 == 0 inside the loop.",
        "pseudo": "START → total = 0 → Loop 1 to 20 → Check even → Add → Print total → END",
        "explanation": "Combining loops and conditions is an important programming skill."
    },


    # ========================================================
    # WORLD 9 — PROBLEM SOLVER PEAK
    # ========================================================

    41: {
        "title": "Search Mission",
        "world": "Problem Solver Peak",
        "difficulty": "Medium",
        "concept": "Searching",
        "question": "Check whether a number exists in a list.",
        "starter_code": "# Search for a number in a list\n",
        "expected": "in",
        "hint": "Python can check membership using in.",
        "help": "Example: if target in numbers:",
        "pseudo": "START → Create list → Get target → Check target in list → Print result → END",
        "explanation": "Searching helps us determine whether a value exists in a collection."
    },

    42: {
        "title": "Count Mission",
        "world": "Problem Solver Peak",
        "difficulty": "Medium",
        "concept": "Frequency",
        "question": "Count how many times a number appears in a list.",
        "starter_code": "# Count occurrences in a list\n",
        "expected": "count",
        "hint": "Lists have a count() method.",
        "help": "Use numbers.count(target).",
        "pseudo": "START → Create list → Count target → Print result → END",
        "explanation": "Frequency problems count how often values occur."
    },

    43: {
        "title": "Second Largest",
        "world": "Problem Solver Peak",
        "difficulty": "Hard",
        "concept": "List Logic",
        "question": "Find the second largest number in a list.",
        "starter_code": "# Find the second largest number\n",
        "expected": "sort",
        "hint": "Sorting can help arrange numbers.",
        "help": "Try sorting the list before accessing the second largest value.",
        "pseudo": "START → Create list → Sort list → Access second largest → Print → END",
        "explanation": "List manipulation can help solve ordering problems."
    },

    44: {
        "title": "Duplicate Detector",
        "world": "Problem Solver Peak",
        "difficulty": "Hard",
        "concept": "Duplicate Detection",
        "question": "Check whether a list contains duplicate values.",
        "starter_code": "# Check for duplicates\n",
        "expected": "set",
        "hint": "Sets store only unique values.",
        "help": "Compare the length of the list with the length of a set.",
        "pseudo": "START → Create list → Convert to set → Compare lengths → Print result → END",
        "explanation": "Sets are useful for detecting duplicate values."
    },

    45: {
        "title": "Peak Challenge",
        "world": "Problem Solver Peak",
        "difficulty": "Hard",
        "concept": "Problem Solving",
        "question": "Find the largest and smallest number in a list.",
        "starter_code": "# Find largest and smallest values\n",
        "expected": "max",
        "hint": "Python has built-in functions for maximum and minimum.",
        "help": "Use both max(numbers) and min(numbers).",
        "pseudo": "START → Create list → Find max → Find min → Print both → END",
        "explanation": "Breaking a problem into smaller operations makes it easier to solve."
    },


    # ========================================================
    # WORLD 10 — PYTHON CHAMPION
    # ========================================================

    46: {
        "title": "Number Reverser",
        "world": "Python Champion",
        "difficulty": "Hard",
        "concept": "Number Logic",
        "question": "Reverse a number using Python logic.",
        "starter_code": "# Reverse a number\n",
        "expected": "while",
        "hint": "Repeatedly extract the last digit.",
        "help": "Use modulo 10 and integer division.",
        "pseudo": "START → Get number → Extract last digit → Build reverse → Remove digit → END",
        "explanation": "Number manipulation problems strengthen logical thinking."
    },

    47: {
        "title": "Prime Hunter",
        "world": "Python Champion",
        "difficulty": "Hard",
        "concept": "Prime Numbers",
        "question": "Check whether a number is prime.",
        "starter_code": "# Check whether a number is prime\n",
        "expected": "for",
        "hint": "A prime number has exactly two factors.",
        "help": "Try dividing the number by values from 2 onwards.",
        "pseudo": "START → Get number → Check divisors → If divisible → Not Prime → Otherwise Prime → END",
        "explanation": "Prime checking combines loops and conditions."
    },

    48: {
        "title": "Fibonacci Journey",
        "world": "Python Champion",
        "difficulty": "Hard",
        "concept": "Fibonacci Series",
        "question": "Print the first 10 numbers of the Fibonacci series.",
        "starter_code": "# Print Fibonacci series\n",
        "expected": "for",
        "hint": "Each number is the sum of the previous two numbers.",
        "help": "Start with a = 0 and b = 1.",
        "pseudo": "START → Set A and B → Loop → Print A → Update values → END",
        "explanation": "The Fibonacci series is a classic problem for practicing loops."
    },

    49: {
        "title": "Python Problem Solver",
        "world": "Python Champion",
        "difficulty": "Hard",
        "concept": "Mixed Challenge",
        "question": "Create a function that finds the sum of all numbers in a list.",
        "starter_code": "# Create a function to find list sum\n",
        "expected": "def",
        "hint": "Combine functions with loops or built-in functions.",
        "help": "Define a function and return the total.",
        "pseudo": "START → Define function → Receive list → Calculate sum → Return result → END",
        "explanation": "Combining multiple concepts is an important step toward solving real problems."
    },

    50: {
        "title": "PyQuest Champion",
        "world": "Python Champion",
        "difficulty": "Hard",
        "concept": "Final Challenge",
        "question": "Write a Python program that takes a list of numbers and prints the largest even number.",
        "starter_code": "# Final PyQuest Challenge\n",
        "expected": "for",
        "hint": "Loop through the numbers and check whether each number is even.",
        "help": "Track the largest even number while looping through the list.",
        "pseudo": "START → Create list → Loop numbers → Check even → Track largest → Print result → END",
        "explanation": "Congratulations! This challenge combines lists, loops, conditions and logical thinking."
    }

}

# ============================================================
# WORLD INFORMATION
# ============================================================

worlds = [

    {
        "number": 1,
        "name": "Python Beginnings",
        "emoji": "🐣",
        "description": "Discover the foundations of Python.",
        "levels": "1–5"
    },

    {
        "number": 2,
        "name": "Loop Valley",
        "emoji": "🔄",
        "description": "Master loops and repetition.",
        "levels": "6–10"
    },

    {
        "number": 3,
        "name": "String Street",
        "emoji": "🔤",
        "description": "Explore the world of text and strings.",
        "levels": "11–15"
    },

    {
        "number": 4,
        "name": "List Land",
        "emoji": "📦",
        "description": "Learn how Python stores collections.",
        "levels": "16–20"
    },

    {
        "number": 5,
        "name": "Logic Kingdom",
        "emoji": "🧠",
        "description": "Build stronger programming logic.",
        "levels": "21–25"
    },

    {
        "number": 6,
        "name": "Function Forest",
        "emoji": "🌲",
        "description": "Learn the power of reusable functions.",
        "levels": "26–30"
    },

    {
        "number": 7,
        "name": "Collection Castle",
        "emoji": "🏰",
        "description": "Master Python collections and data structures.",
        "levels": "31–35"
    },

    {
        "number": 8,
        "name": "Challenge Arena",
        "emoji": "⚔️",
        "description": "Face exciting mixed Python challenges.",
        "levels": "36–40"
    },

    {
        "number": 9,
        "name": "Problem Solver Peak",
        "emoji": "🏔️",
        "description": "Strengthen your problem-solving skills.",
        "levels": "41–45"
    },

    {
        "number": 10,
        "name": "Python Champion",
        "emoji": "🏆",
        "description": "Complete the final PyQuest challenges.",
        "levels": "46–50"
    }

]


# ============================================================
# GET CURRENT PLAYER
# ============================================================

def get_current_player():

    if "user_id" not in session:
        return None

    connection = get_db()

    player = connection.execute(

        """
        SELECT *
        FROM users
        WHERE id = ?
        """,

        (session["user_id"],)

    ).fetchone()

    connection.close()

    return player


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    player = get_current_player()

    return render_template(
        "index.html",
        user=player,
        player=player
    )


# ============================================================
# START QUEST
# ============================================================

@app.route("/start")
def start():

    if "user_id" in session:
        return redirect(url_for("map_page"))

    return redirect(url_for("create_profile"))


# ============================================================
# CREATE PLAYER PROFILE
# ============================================================

@app.route(
    "/create-profile",
    methods=["GET", "POST"]
)
def create_profile():

    if "user_id" in session:
        return redirect(url_for("map_page"))

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        if not name:

            return render_template(
                "create_profile.html",
                error="Please enter your name to begin your quest 🐍"
            )

        name = name[:50]

        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(

            """
            INSERT INTO users (

                name,
                current_level,
                completed_levels,
                streak,
                certificates,
                xp,
                last_active,
                assessment_score,
                skill_level

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (
                name,
                1,
                0,
                0,
                0,
                0,
                "",
                0,
                ""
            )

        )

        user_id = cursor.lastrowid

        connection.commit()
        connection.close()

        session["user_id"] = user_id

        return redirect(
            url_for("assessment")
        )

    return render_template(
        "create_profile.html"
    )


# ============================================================
# ASSESSMENT
# ============================================================

@app.route(
    "/assessment",
    methods=["GET", "POST"]
)
def assessment():

    if "user_id" not in session:
        return redirect(url_for("start"))

    if request.method == "POST":

        score = 0

        for question, correct_answer in assessment_answers.items():

            user_answer = request.form.get(
                question,
                ""
            )

            if user_answer.strip().lower() == correct_answer.lower():
                score += 1

        if score <= 12:

            skill_level = "Beginner"
            starting_level = 1

        elif score <= 22:

            skill_level = "Intermediate"
            starting_level = 6

        else:

            skill_level = "Advanced"
            starting_level = 11

        connection = get_db()

        connection.execute(

            """
            UPDATE users

            SET assessment_score = ?,
                skill_level = ?,
                current_level = ?

            WHERE id = ?
            """,

            (
                score,
                skill_level,
                starting_level,
                session["user_id"]
            )

        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("assessment_result")
        )

    return render_template(
        "assessment.html"
    )


# ============================================================
# ASSESSMENT RESULT
# ============================================================

@app.route("/assessment-result")
def assessment_result():

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))


    return render_template(

        "assessment_result.html",

        user=player,
        player=player,

        score=player["assessment_score"],

        total_questions=30

    )


# ============================================================
# MAP
# ============================================================
# ============================================================
# QUEST MAP
# ============================================================

@app.route("/map")
def map_page():

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    # Make sure current level is always an integer
    current_level = int(player["current_level"] or 1)

    # ========================================================
    # CREATE LEVEL STATUS
    # ========================================================

    map_levels = []

    for level_id, level_data in levels.items():

        # Convert string IDs to integers
        level_id = int(level_id)

        level_info = dict(level_data)

        level_info["id"] = level_id


        # ----------------------------------------------------
        # COMPLETED LEVEL
        # ----------------------------------------------------

        if level_id < current_level:

            level_info["completed"] = True
            level_info["current"] = False
            level_info["locked"] = False


        # ----------------------------------------------------
        # CURRENT LEVEL
        # ----------------------------------------------------

        elif level_id == current_level:

            level_info["completed"] = False
            level_info["current"] = True
            level_info["locked"] = False


        # ----------------------------------------------------
        # LOCKED LEVEL
        # ----------------------------------------------------

        else:

            level_info["completed"] = False
            level_info["current"] = False
            level_info["locked"] = True


        map_levels.append(level_info)


    # ========================================================
    # CALCULATE WORLD PROGRESS
    # ========================================================

    processed_worlds = []

    for world in worlds:

        world_info = dict(world)

        world_name = world_info["name"]

        # Find all levels belonging to this world
        world_levels = [

            level for level in map_levels

            if level.get("world") == world_name

        ]


        # Total levels in this world
        world_info["total"] = len(world_levels)


        # Completed levels in this world
        world_info["completed"] = sum(

            1

            for level in world_levels

            if level.get("completed")

        )


        # Progress percentage
        if world_info["total"] > 0:

            world_info["progress_percentage"] = (

                world_info["completed"]
                /
                world_info["total"]
                *
                100

            )

        else:

            world_info["progress_percentage"] = 0


        processed_worlds.append(world_info)


    # ========================================================
    # RENDER MAP
    # ========================================================

    return render_template(

        "map.html",

        player=player,

        user=player,

        levels=map_levels,

        worlds=processed_worlds

    )

    
# ============================================================
# CONCEPT INTRODUCTION
# ============================================================

@app.route("/concept/<int:level_id>")
def concept(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    current_level = player["current_level"] or 1

    if level_id > current_level:
        return redirect(url_for("map_page"))

    return render_template(

        "concept.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player

    )
# ============================================================
# LEVEL
# ============================================================

# ============================================================
# LEVEL
# ============================================================

@app.route("/level/<int:level_id>")
def level(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    # Prevent access to locked levels
    current_level = player["current_level"] or 1

    if level_id > current_level:
        return redirect(url_for("map_page"))

    return render_template(

        "level.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player

    )
    # --------------------------------------------------------
    # POST REQUEST — RUN & SUBMIT
    # --------------------------------------------------------

    code = request.form.get("code", "").strip()

    # Empty code check
    if not code:

        return render_template(

            "level.html",

            level_id=level_id,

            level=level_data,

            player=player,

            user=player,

            code=code,

            error="Please write some Python code before submitting! 🐍"

        )

    # --------------------------------------------------------
    # BASIC ANSWER VALIDATION
    # --------------------------------------------------------

    expected_answer = level_data.get("answer", "")

    # If answer checking data exists
    if expected_answer:

        if expected_answer.lower() not in code.lower():

            return render_template(

                "level.html",

                level_id=level_id,

                level=level_data,

                player=player,

                user=player,

                code=code,

                error="Hmm... that's not quite right yet. Check your solution and try again! 💜"

            )

    # --------------------------------------------------------
    # LEVEL COMPLETED
    # --------------------------------------------------------

    conn = get_db()

    conn.execute(
        """
        UPDATE users
        SET current_level = ?,
        completed_levels = ?,
        xp = ?
        WHERE id = ?
        """,
        (
        new_current_level,
        new_completed_levels,
        new_xp,
        player["id"]
        )
    )

    conn.commit()
    
    conn.close()


    # --------------------------------------------------------
    # REDIRECT TO NEXT LEVEL / MAP
    # --------------------------------------------------------

    if level_id < len(levels):

        return redirect(

            url_for(

                "level",

                level_id=level_id + 1

            )

        )

    return redirect(

        url_for("map_page")

    )
# ============================================================
# SMART CODE VALIDATION
# ============================================================

def validate_code(level_id, code):

    code_lower = code.lower().strip()


    # ========================================================
    # LEVEL 1
    # ========================================================

    if level_id == 1:

        return (
            "print" in code_lower
            and "hello, python!" in code_lower
        )


    # ========================================================
    # LEVEL 2
    # ========================================================

    elif level_id == 2:

        return (
            "name" in code_lower
            and "=" in code
        )


    # ========================================================
    # LEVEL 3
    # ========================================================

    elif level_id == 3:

        return (
            "=" in code
            and "+" in code
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 4
    # ========================================================

    elif level_id == 4:

        return (
            "input" in code_lower
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 5
    # ========================================================

    elif level_id == 5:

        return (
            "if" in code_lower
            and "%" in code
            and "2" in code
            and "else" in code_lower
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 6
    # ========================================================

    elif level_id == 6:

        return (
            "for" in code_lower
            and "range" in code_lower
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 7
    # ========================================================

    elif level_id == 7:

        return (
            "for" in code_lower
            and "range" in code_lower
            and (
                "+=" in code
                or "total = total +" in code_lower
            )
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 8
    # ========================================================

    elif level_id == 8:

        return (
            "len(" in code_lower
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 9
    # ========================================================

    elif level_id == 9:

        return (
            "[" in code
            and "]" in code
            and "print" in code_lower
        )


    # ========================================================
    # LEVEL 10
    # ========================================================

    elif level_id == 10:

        return (

            (
                "if" in code_lower
                and ">" in code
                and "print" in code_lower
            )

            or

            (
                "max(" in code_lower
                and "print" in code_lower
            )

        )


    # ========================================================
    # LEVELS 11–50
    # TEMPORARY DEFAULT VALIDATION
    # ========================================================

    else:

        expected_keyword = (
            levels
            .get(level_id, {})
            .get("expected", "")
            .lower()
        )


        return (
            bool(expected_keyword)
            and expected_keyword in code_lower
        )


# ============================================================
# RUN PYTHON CODE
# ============================================================

@app.route("/run_code/<int:level_id>", methods=["POST"])
def run_code(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))


    # --------------------------------------------------------
    # GET USER CODE
    # --------------------------------------------------------

    code = request.form.get(
        "code",
        ""
    ).strip()


    # --------------------------------------------------------
    # EMPTY CODE
    # --------------------------------------------------------

    if not code:

        return render_template(

            "level.html",

            level_id=level_id,

            level=level_data,

            player=player,

            user=player,

            output="",

            run_error="Please write some Python code first! 🐍"

        )


    # --------------------------------------------------------
    # RUN CODE SAFELY WITH TIMEOUT
    # --------------------------------------------------------

    try:

        result = subprocess.run(

            ["python", "-c", code],

            capture_output=True,

            text=True,

            timeout=5

        )


        output = result.stdout.strip()

        run_error = result.stderr.strip()


        # If there is no output

        if not output and not run_error:

            output = "Code ran successfully — no output."


    except subprocess.TimeoutExpired:

        output = ""

        run_error = (
            "⏱️ Your code took too long to run."
        )


    except Exception as error:

        output = ""

        run_error = str(error)


    # --------------------------------------------------------
    # RETURN TO LEVEL PAGE
    # --------------------------------------------------------

    return render_template(

        "level.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player,

        output=output,

        run_error=run_error,

        code=code

    )


# ============================================================
# CHECK CODE
# ============================================================

@app.route(
    "/check/<int:level_id>",
    methods=["POST"]
)
def check_code(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))


    # --------------------------------------------------------
    # PREVENT COMPLETING LOCKED LEVELS
    # --------------------------------------------------------

    current_level = player["current_level"] or 1

    if level_id > current_level:
        return redirect(url_for("map_page"))


    # --------------------------------------------------------
    # GET USER CODE
    # --------------------------------------------------------

    code = request.form.get(
        "code",
        ""
    ).strip()


    # --------------------------------------------------------
    # VALIDATE CODE
    # --------------------------------------------------------

    success = validate_code(
        level_id,
        code
    )


    # ========================================================
    # SUCCESS
    # ========================================================

    if success:

        connection = get_db()

        user = connection.execute(

            """
            SELECT *

            FROM users

            WHERE id = ?
            """,

            (
                session["user_id"],
            )

        ).fetchone()


        completed_levels = user[
            "completed_levels"
        ] or 0

        if level_id > completed_levels:
            completed_levels = level_id


        next_level = max(

            user["current_level"] or 1,

            level_id + 1

        )


        current_xp = user[
            "xp"
        ] or 0


        existing_progress = connection.execute(

            """
            SELECT *

            FROM progress

            WHERE user_id = ?

            AND level = ?

            AND completed = 1
            """,

            (
                session["user_id"],
                level_id
            )

        ).fetchone()


        if existing_progress:

            new_xp = current_xp

        else:

            new_xp = current_xp + 10


        # ====================================================
        # STREAK
        # ====================================================

        today = date.today().isoformat()

        last_active = user[
            "last_active"
        ] or ""

        new_streak = user[
            "streak"
        ] or 0


        if last_active != today:

            if last_active:

                try:

                    previous_date = datetime.strptime(

                        last_active,

                        "%Y-%m-%d"

                    ).date()


                    difference = (

                        date.today()

                        - previous_date

                    ).days


                    if difference == 1:

                        new_streak += 1

                    elif difference > 1:

                        new_streak = 1


                except ValueError:

                    new_streak = 1

            else:

                new_streak = 1


        # ====================================================
        # UPDATE PLAYER
        # ====================================================

        connection.execute(

            """
            UPDATE users

            SET completed_levels = ?,
                current_level = ?,
                xp = ?,
                streak = ?,
                last_active = ?

            WHERE id = ?
            """,

            (
                completed_levels,
                next_level,
                new_xp,
                new_streak,
                today,
                session["user_id"]
            )

        )


        # ====================================================
        # SAVE PROGRESS
        # ====================================================

        if existing_progress:

            connection.execute(

                """
                UPDATE progress

                SET completed = 1

                WHERE user_id = ?

                AND level = ?
                """,

                (
                    session["user_id"],
                    level_id
                )

            )

        else:

            connection.execute(

                """
                INSERT INTO progress (

                    user_id,
                    level,
                    completed

                )

                VALUES (?, ?, ?)
                """,

                (
                    session["user_id"],
                    level_id,
                    1
                )

            )


        connection.commit()


        updated_player = connection.execute(

            """
            SELECT *

            FROM users

            WHERE id = ?
            """,

            (
                session["user_id"],
            )

        ).fetchone()


        connection.close()


        return render_template(

            "success.html",

            level_id=level_id,

            level=level_data,

            next_level=level_id + 1,

            player=updated_player,

            user=updated_player

        )


    # ========================================================
    # FAILED ATTEMPT
    # ========================================================

    return render_template(

        "level.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player,

        error="Not quite! Try again 💡"

    )


# ============================================================
# HINT
# ============================================================

@app.route("/hint/<int:level_id>")
def hint(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    return render_template(

        "level.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player,

        show_hint=True

    )


# ============================================================
# HELP
# ============================================================

@app.route("/help/<int:level_id>")
def help_level(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    return render_template(

        "level.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player,

        show_help=True

    )


# ============================================================
# PSEUDOCODE
# ============================================================

@app.route("/pseudo/<int:level_id>")
def pseudo(level_id):

    level_data = levels.get(level_id)

    if not level_data:
        return redirect(url_for("map_page"))

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    return render_template(

        "level.html",

        level_id=level_id,

        level=level_data,

        player=player,

        user=player,

        show_pseudo=True

    )


# ============================================================
# STREAK
# ============================================================

@app.route("/streak")
def streak():

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    return render_template(

        "index.html",

        user=player,

        player=player

    )


# ============================================================
# CERTIFICATE
# ============================================================

@app.route("/certificate")
def certificate():

    player = get_current_player()

    if player is None:
        return redirect(url_for("index"))

    current_date = date.today().strftime(
        "%B %d, %Y"
    )

    return render_template(

        "certificate.html",

        user=player,

        player=player,

        current_date=current_date

    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# ERROR 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """

    <div style="

        text-align: center;
        padding: 100px;
        font-family: Arial;

    ">

        <h1>🐍 404</h1>

        <h2>
            Oops! This Python path doesn't exist.
        </h2>

        <a href="/">
            Return to PyQuest
        </a>

    </div>

    """, 404


# ============================================================
# ERROR 500
# ============================================================

@app.errorhandler(500)
def internal_error(error):

    return """

    <div style="

        text-align: center;
        padding: 100px;
        font-family: Arial;

    ">

        <h1>🐍 Something went wrong!</h1>

        <h2>
            PyQuest is trying to fix itself...
        </h2>

        <a href="/">
            Return Home
        </a>

    </div>

    """, 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_database()

    print()

    print("======================================")

    print("        🐍 PYQUEST IS STARTING")

    print("        Learn Python. Level Up.")

    print("======================================")

    print()

    app.run(
        debug=True
    )