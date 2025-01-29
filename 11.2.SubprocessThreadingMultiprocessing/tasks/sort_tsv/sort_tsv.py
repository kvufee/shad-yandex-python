import subprocess

from pathlib import Path


def python_sort(file_in: Path, file_out: Path) -> None:
    """
    Sort tsv file using python built-in sort
    :param file_in: tsv file to read from
    :param file_out: tsv file to write to
    """
    with file_in.open('r') as f_in:
        lines = f_in.readlines()

    sorted_lines = sorted(lines, key=lambda line: (int(line.split('\t')[1]), line.split('\t')[0]))

    with file_out.open('w') as f_out:
        f_out.writelines(sorted_lines)


def util_sort(file_in: Path, file_out: Path) -> None:
    """
    Sort tsv file using sort util
    :param file_in: tsv file to read from
    :param file_out: tsv file to write to
    """
    sort_command = [
        'sort',
        '-t', '\t',
        '-k2,2n',
        '-k1,1',
        str(file_in),
        '-o', str(file_out)
    ]
    subprocess.run(sort_command, check=True)
