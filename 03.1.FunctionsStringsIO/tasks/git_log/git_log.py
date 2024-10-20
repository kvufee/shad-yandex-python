import typing as tp


def reformat_git_log(inp: tp.IO[str], out: tp.IO[str]) -> None:
    """Reads git log from `inp` stream, reformats it and prints to `out` stream

    Expected input format: `<sha-1>\t<date>\t<author>\t<email>\t<message>`
    Output format: `<first 7 symbols of sha-1>.....<message>`
    """
    for i in inp:
        parts = i.strip().split('\t')

        sha = parts[0][:7]
        mess = parts[4]
        dots = '.' * (73 - len(mess))

        result = f'{sha}{dots}{mess}\n'

        out.write(result)
