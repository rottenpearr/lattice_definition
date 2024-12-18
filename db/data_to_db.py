from pathlib import Path
import subprocess


def parse_txt(lattice_type_id_path):
    with open(lattice_type_id_path, "r") as file:
        id = file.readline()
    return id


def main():  # Здесь сделать 1 по имени или все через glob????  xyz_files_path = Path("../data/xyz")
    json_file_path = Path("../data/json/1000041.json")
    lattice_type_id_path = Path("lattice_type_id.txt")
    xyz_file_path = Path("../data/xyz/1000041.xyz")

    subprocess.run(["python", Path("json_to_db.py"), json_file_path])

    lattice_type_id = parse_txt(lattice_type_id_path)

    subprocess.run(["python", Path("xyz_to_db.py"), xyz_file_path, str(lattice_type_id)])

if __name__ == "__main__":
    main()