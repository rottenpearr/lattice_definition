from ase.io import read, write


def convert_cif_to_xyz(input_cif, output_xyz):
    try:
        # read автоматически парсит CIF, применяет симметрии
        # и переводит координаты в декартовы (Angstrom)
        atoms = read(input_cif)

        # write автоматически формирует нужную структуру .xyz файла
        write(output_xyz, atoms)

        print(f"Конвертация завершена. Найдено атомов: {len(atoms)}")
    except Exception as e:
        print(f"Ошибка при конвертации: {e}")


# Использование
convert_cif_to_xyz('NaCl.cif', 'NaCl_Ass_artyom.xyz')
