from pathlib import Path
import subprocess
from glob import glob


def parse_txt(json_additional_data_path):
    with open(json_additional_data_path, "r") as file:
        lattice_id = file.readline()
        substance_id = file.readline()
    return [lattice_id, substance_id]


def main():
    subprocess.run(["python", Path("db_init.py")])
    subprocess.run(["python", Path("lattice_types_init.py")])

    print("Запись данных из всех файлов в базу данных:")
    files_path = Path("../../data/json")
    files = glob(str(files_path / "*.json"))
    for file_path in files:
        filename = Path(file_path).stem
        print(f"Запись файлов {filename}.json и {filename}.xyz")
        json_file_path = Path(f"../data/json/{filename}.json")
        json_additional_data_path = Path("json_additional_data.txt")
        xyz_file_path = Path(f"../data/xyz/{filename}.xyz")

        subprocess.run(["python", Path("json_to_db.py"), json_file_path])

        lattice_type_id, substance_id = parse_txt(json_additional_data_path)

        subprocess.run(["python", Path("xyz_to_db.py"), xyz_file_path, str(lattice_type_id), str(substance_id)])

    print("База данных полностью инициализирована.")

if __name__ == "__main__":
    main()
