import random


def write_nacl_xyz_exact(N=7, a=5.6402, filename="NaCl.xyz", extended=True):
    """
    Генерирует файл XYZ для NaCl с точно N атомами по каждой оси. В обычных координатах (по постоянной).
    """
    atoms = []
    # Шаг между атомами в решётке NaCl
    step = a / 2

    for i in range(N):
        for j in range(N):
            for k in range(N):
                # Сумма индексов определяет тип атома
                if (i + j + k) % 2 == 0:
                    atoms.append(("Cl", i*step, j*step, k*step))
                else:
                    atoms.append(("Na", i*step, j*step, k*step))

    with open(filename, "w") as f:
        f.write(f"{len(atoms)}\n")
        if extended:
            f.write(f'Lattice="{N*step*2} 0 0 0 {N*step*2} 0 0 0 {N*step*2}" Properties=species:S:1:pos:R:3\n')
        else:
            f.write(f"NaCl rock-salt; a={a} Ang; {N} atoms per axis\n")
        for s, x, y, z in atoms:
            f.write(f"{s} {x:.6f} {y:.6f} {z:.6f}\n")


def write_nacl_xyz_inaccurate(N=7, a=5.6402, filename="NaCl-innacurate.xyz", extended=True, inaccuracy=1e-6):
    """
    Генерирует файл XYZ для NaCl с точно N атомами по каждой оси.
    """
    atoms = []
    # Шаг между атомами в решётке NaCl
    step = a / 2

    for i in range(N):
        for j in range(N):
            for k in range(N):
                # Сумма индексов определяет тип атома
                x_shift, y_shift, z_shift = random.uniform(-inaccuracy, inaccuracy), random.uniform(-inaccuracy, inaccuracy), random.uniform(-inaccuracy, inaccuracy)
                if (i + j + k) % 2 == 0:
                    atoms.append(("Cl", i*step+x_shift, j*step+y_shift, k*step+z_shift))
                else:
                    atoms.append(("Na", i*step+x_shift, j*step+y_shift, k*step+z_shift))

    with open(filename, "w") as f:
        f.write(f"{len(atoms)}\n")
        if extended:
            f.write(f'Lattice="{N*step*2} 0 0 0 {N*step*2} 0 0 0 {N*step*2}" Properties=species:S:1:pos:R:3\n')
        else:
            f.write(f"NaCl rock-salt; a={a} Ang; {N} atoms per axis\n")
        for s, x, y, z in atoms:
            f.write(f"{s} {x:.6f} {y:.6f} {z:.6f}\n")
        print(f"Finished!")


def write_un_xyz_exact(N=3, a=4.890, filename="UN.xyz", extended=True):
    """
    Генерирует файл XYZ для UN (нитрид урана) с точно N атомами по каждой оси.
    UN имеет структуру типа NaCl (rock-salt, Fm-3m).

    Параметры:
    - N: количество атомов по каждой оси (обычно нечетное число: 3, 5, 7)
    - a: постоянная решетки в ангстремах (по умолчанию 4.890 Å)
    - filename: имя выходного файла
    - extended: использовать расширенный формат с информацией о решетке
    """
    atoms = []
    step = a / 2  # Шаг между атомами

    for i in range(N):
        for j in range(N):
            for k in range(N):
                x, y, z = i * step, j * step, k * step
                # Сумма индексов определяет тип атома
                if (i + j + k) % 2 == 0:
                    atoms.append(("N", x, y, z))
                else:
                    atoms.append(("U", x, y, z))

    with open(filename, "w") as f:
        f.write(f"{len(atoms)}\n")
        if extended:
            lattice_size = N * step * 2
            f.write(
                f'Lattice="{lattice_size} 0 0 0 {lattice_size} 0 0 0 {lattice_size}" Properties=species:S:1:pos:R:3\n')
        else:
            f.write(f"N U\n")

        for s, x, y, z in atoms:
            f.write(f"{s:>2s} {x:11.6f} {y:11.6f} {z:11.6f}\n")


def write_uc_xyz_exact(N=3, a=4.960, filename="UC.xyz", extended=True):
    """
    Генерирует файл XYZ для UC (карбид урана) с точно N атомами по каждой оси.
    UC имеет структуру типа NaCl (rock-salt, Fm-3m).

    Параметры:
    - N: количество атомов по каждой оси (обычно нечетное число: 3, 5, 7)
    - a: постоянная решетки в ангстремах (по умолчанию 4.960 Å)
    - filename: имя выходного файла
    - extended: использовать расширенный формат с информацией о решетке
    """
    atoms = []
    step = a / 2  # Шаг между атомами

    for i in range(N):
        for j in range(N):
            for k in range(N):
                x, y, z = i * step, j * step, k * step
                # Сумма индексов определяет тип атома
                if (i + j + k) % 2 == 0:
                    atoms.append(("C", x, y, z))
                else:
                    atoms.append(("U", x, y, z))

    with open(filename, "w") as f:
        f.write(f"{len(atoms)}\n")
        if extended:
            lattice_size = N * step * 2
            f.write(
                f'Lattice="{lattice_size} 0 0 0 {lattice_size} 0 0 0 {lattice_size}" Properties=species:S:1:pos:R:3\n')
        else:
            f.write(f"C U\n")

        for s, x, y, z in atoms:
            f.write(f"{s:>2s} {x:11.6f} {y:11.6f} {z:11.6f}\n")


if __name__ == "__main__":
    from pathlib import Path
    OUT = Path(__file__).parent.parent.parent.parent / "data" / "structures" / "macro" / "source"
    OUT.mkdir(parents=True, exist_ok=True)

    write_nacl_xyz_exact(N=3, a=5.6402, filename=str(OUT / "NaCl_3x3x3.xyz"), extended=True)
    write_nacl_xyz_exact(N=5, a=5.6402, filename=str(OUT / "NaCl_5x5x5.xyz"), extended=True)
    write_nacl_xyz_exact(N=7, a=5.6402, filename=str(OUT / "NaCl_7x7x7.xyz"), extended=True)

    write_un_xyz_exact(N=3, filename=str(OUT / "UN_3x3x3.xyz"), extended=False)
    write_un_xyz_exact(N=5, filename=str(OUT / "UN_5x5x5.xyz"), extended=False)
    write_un_xyz_exact(N=7, filename=str(OUT / "UN_7x7x7.xyz"), extended=False)

    write_uc_xyz_exact(N=3, filename=str(OUT / "UC_3x3x3.xyz"), extended=False)
    write_uc_xyz_exact(N=5, filename=str(OUT / "UC_5x5x5.xyz"), extended=False)
    write_uc_xyz_exact(N=7, filename=str(OUT / "UC_7x7x7.xyz"), extended=False)

