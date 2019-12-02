import svc.svc as svc
from svc.mongo_setup import global_init

global_init()

def main():

    name = input("Enter Name: ")
    value = input("Enter Value: ")
    rarity = input("Enter Rarity (0-3): ")

    description = input("(OPTIONAL) Enter Description: ")

    try:
        int(value)
    except ValueError:
        print("Value should be a Number")
        return

    
    svc.create_base_item(name=name, value=value, rarity=rarity, description=description)
    


if __name__ == "__main__":
    main()