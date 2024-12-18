from pathlib import Path
import subprocess
from glob import glob


def parse_txt(lattice_type_id_path):
    with open(lattice_type_id_path, "r") as file:
        id = file.readline()
    return id


def main():
    files_path = Path("../data/json")
    files = glob(str(files_path / "*.json"))
    for file_path in files:
        filename = Path(file_path).stem
        json_file_path = Path(f"../data/json/{filename}.json")
        lattice_type_id_path = Path("lattice_type_id.txt")
        xyz_file_path = Path(f"../data/xyz/{filename}.xyz")

        subprocess.run(["python", Path("json_to_db.py"), json_file_path])

        lattice_type_id = parse_txt(lattice_type_id_path)

        subprocess.run(["python", Path("xyz_to_db.py"), xyz_file_path, str(lattice_type_id)])

if __name__ == "__main__":
    main()