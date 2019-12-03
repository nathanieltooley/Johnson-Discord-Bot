import svc.svc as svc
import sys
from svc.mongo_setup import global_init

global_init()

def main():

    name = input("Enter Name: ")
    _id = input("Enter ID: ")
    value = input("Enter Value: ")
    rarity = input("Enter Rarity (Common, Uncommon, Rare): ")

    description = input("(OPTIONAL) Enter Description: ")

    try:
        int(value)
    except ValueError:
        print("Value should be a Number")
        return

    
    svc.create_base_item(item_id=_id, name=name, value=value, rarity=rarity, description=description)
    


if __name__ == "__main__":
    main()