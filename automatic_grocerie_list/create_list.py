import os
import argparse
from food_list import FoodList, Livsmedelsverket


def main():
    # Parse command-line arguments
    print("LEEEEETS GOOOOOOOOOOOOOOOOOOOOOO!!!!!!!!!!!!!!!")
    parser = argparse.ArgumentParser(description="Manage your food list")
    parser.add_argument('--delete', nargs='+', help='Item(s) to delete from the food list')
    parser.add_argument('--add', nargs='+', help='Item(s) to add to the food list')
    parser.add_argument('--image_path', help='Path to the image of the receipt')
    parser.add_argument('--spreadsheet_path', help='Path to the spreadsheet with the food list')
    args = parser.parse_args()

    # Initialize FoodList instance
    file_path = os.path.join(os.getcwd(),args.spreadsheet_path)
    print(file_path)
    main_list = FoodList()

    # If --delete is provided, delete the specified items
    if args.delete:
        items_to_remove = args.delete
        main_list.delete_item(file_path, items_to_remove)

    elif args.add:
        items_to_add = args.add
        main_list.add_item(items_to_add)
        main_list.save_items(file_path)

    else:
        # Perform your regular script actions here if no command-line arguments are provided
        print("No command provided. Adding food from receipts...")

        # Read file from livsmedelverket

        file_name =  os.path.join(os.getcwd(),"data","Livsmedel.xlsx")  # Assuming this file is in the current working directory
        livsmedelslista = Livsmedelsverket()
        livsmedelslista.read_excel_file(os.path.join(os.getcwd(), file_name))
        livsmedelslista.clean()

        # Read food from receipt and compare with reference
        for kvitto in os.listdir(os.path.join(os.getcwd(), args.image_path)):
            new_list = FoodList()
            new_list.read_receipt(os.path.join(os.getcwd(), args.image_path), kvitto)
            main_list.add_item(livsmedelslista.filter_food(new_list.grocery_list))

        # Save new items to the Excel file
        main_list.save_items(file_path)

if __name__ == "__main__":
    main()
