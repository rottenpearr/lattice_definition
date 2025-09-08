def write_nacl_xyz_exact(N=7, a=5.6402, filename="NaCl.xyz", extended=True):
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


if __name__ == "__main__":
    write_nacl_xyz_exact(N=7, a=5.6402, filename="../../data/NaCl/NaCl_7x7x7.xyz", extended=True)
