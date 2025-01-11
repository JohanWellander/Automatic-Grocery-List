#import tesseract
from PIL import Image
import os
import csv
import re
import string
import pandas as pd
import xlsxwriter
import openpyxl
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Users/JWELLAND/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

class FoodList():
    def __init__(self):
        self.grocery_list = []
        self.workbook = openpyxl.Workbook()

    def delete_item(self, file_path, item: str):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            if isinstance(item, list):
                for i in item:
                    # Remove rows where the 'Livsmedel' column contains `i`
                    df = df[df['Livsmedel'] != i]
                    print(f"Deleted {i}")
            else:
                df = df[df['Livsmedel'] != item]
                print(f"Deleted {item}")

            # Save the updated DataFrame back to the Excel file
            df.to_excel(file_path, index=False)
            print(f"Updated file saved to {file_path}")
        else:
            print(f"No file exists at {file_path}")

    def add_item(self, item: str):
        if isinstance(item, list):
            for i in item:
                self.grocery_list.append(i.lower())
        else:
            self.grocery_list.append(item.lower())

    def save_items(self, file_path):
        self.grocery_list.sort()
        if os.path.exists(file_path):
            print("Adding groceries to list")
            df = pd.read_excel(file_path)
            df = df[df['Livsmedel'].notna() & (df['Livsmedel'] != '')]
            new_items = []

            for word in self.grocery_list:
                if word not in df["Livsmedel"].values:
                    new_items.append({"Livsmedel": word})

            if new_items:
                new_items_df = pd.DataFrame(new_items)
                print(f"New items added: {new_items_df['Livsmedel'].tolist()}")
                df = pd.concat([df, new_items_df], ignore_index=True)
                df.to_excel(file_path, index=False)
            else:
                print("Nothing new to add, bye bye")
        else:
            print("Creating main_food_list.xlsx with existing food")
            self.grocery_list.sort()
            df = pd.DataFrame({"Livsmedel": self.grocery_list})
            df.to_excel(file_path, index=False)
            print(f"Created {file_path} with initial data.")

    def read_receipt(self, dir, image):
        image_path = os.path.join(dir, image)
        image = Image.open(image_path)
        self.grocery_list = pytesseract.image_to_string(image, lang="swe").lower().split()

class Livsmedelsverket():
    def __init__(self):
        self.food_list = pd.DataFrame()

    def read_excel_file(self, file_path):
        livsmedelslista = pd.read_excel(io=file_path, usecols="A", skiprows=2)
        food_list = [word for item in livsmedelslista["Livsmedelsnamn"] for word in self.remove_non_letters(item).split()]
        food_list = [row for row in food_list if all(len(word) >= 3 for word in row.split())]
        food_list = [word.lower() for word in food_list]
        self.food_list = pd.DataFrame({"Livsmedel": food_list})

    def remove_non_letters(self, input_string):
        cleaned_string = re.sub(r'[^a-öA-Ö\s]', '', input_string)
        return cleaned_string

    def clean(self):
        cleaned_words = []
        bad_words = ["röd", "gul", "svart", "grön", "blå", "ica", "och", "för", "eko", "brun", "pulver"]
        for word in self.food_list["Livsmedel"]:
            if word not in bad_words:
                cleaned_words.append(word)
        self.food_list = pd.DataFrame({"Livsmedel": cleaned_words})

    def filter_food(self, new_list: list):
        filtered_food = self.food_list[self.food_list["Livsmedel"].isin(new_list)]
        return list(filtered_food.Livsmedel.unique())
