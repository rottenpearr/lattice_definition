from pathlib import Path
import subprocess
from glob import glob

ROOT = Path(__file__).parent.parent.parent


def parse_txt(json_additional_data_path):
    with open(json_additional_data_path, "r") as file:
        lattice_id = file.readline()
        substance_id = file.readline()
    return [lattice_id, substance_id]


def main():
    subprocess.run(["python", ROOT / "cris" / "db" / "schema" / "db_init.py"])
    subprocess.run(["python", ROOT / "cris" / "db" / "schema" / "lattice_types_init.py"])

    print("Запись данных из всех файлов в базу данных:")
    files_path = ROOT / "data" / "db" / "json"
    files = glob(str(files_path / "*.json"))
    json_additional_data_path = ROOT / "cris" / "db" / "importers" / "json_additional_data.txt"

    for file_path in files:
        filename = Path(file_path).stem
        print(f"Запись файлов {filename}.json и {filename}.xyz")
        json_file_path = ROOT / "data" / "db" / "json" / f"{filename}.json"
        xyz_file_path  = ROOT / "data" / "db" / "xyz"  / f"{filename}.xyz"

        subprocess.run(["python", ROOT / "cris" / "db" / "importers" / "json_to_db.py", json_file_path])

        lattice_type_id, substance_id = parse_txt(json_additional_data_path)

        subprocess.run(["python", ROOT / "cris" / "db" / "importers" / "xyz_to_db.py",
                        xyz_file_path, str(lattice_type_id).strip(), str(substance_id).strip()])

    print("База данных полностью инициализирована.")

if __name__ == "__main__":
    main()
