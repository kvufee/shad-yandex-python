import zlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BlobType(Enum):
    """Helper class for holding blob type"""
    COMMIT = b'commit'
    TREE = b'tree'
    DATA = b'blob'

    @classmethod
    def from_bytes(cls, type_: bytes) -> 'BlobType':
        for member in cls:
            if member.value == type_:
                return member
        assert False, f'Unknown type {type_.decode("utf-8")}'


@dataclass
class Blob:
    """Any blob holder"""
    type_: BlobType
    content: bytes


@dataclass
class Commit:
    """Commit blob holder"""
    tree_hash: str
    parents: list[str]
    author: str
    committer: str
    message: str


@dataclass
class Tree:
    """Tree blob holder"""
    children: dict[str, Blob]


def read_blob(path: Path) -> Blob:
    """
    Read blob-file, decompress and parse header
    :param path: path to blob-file
    :return: blob-file type and content
    """
    with path.open('rb') as f:
        compressed_data = f.read()

    decompressed_data = zlib.decompress(compressed_data)

    header_end = decompressed_data.index(b'\x00')
    header = decompressed_data[:header_end].decode('utf-8')
    blob_type_str, size_str = header.split()

    content = decompressed_data[header_end + 1:]
    blob_type = BlobType.from_bytes(blob_type_str.encode('utf-8'))

    return Blob(type_=blob_type, content=content)


def traverse_objects(obj_dir: Path) -> dict[str, Blob]:
    """
    Traverse directory with git objects and load them
    :param obj_dir: path to git "objects" directory
    :return: mapping from hash to blob with every blob found
    """
    objects = {}
    for subdir in obj_dir.iterdir():
        if subdir.is_dir():
            for file in subdir.iterdir():
                hash_prefix = subdir.name
                hash_suffix = file.name
                full_hash = hash_prefix + hash_suffix
                blob = read_blob(file)
                objects[full_hash] = blob

    return objects


def parse_commit(blob: Blob) -> Commit:
    """
    Parse commit blob
    :param blob: blob with commit type
    :return: parsed commit
    """
    tree_hash = ''
    parents = []
    author = ''
    committer = ''
    message = ''

    assert blob.type_ == BlobType.COMMIT
    lines = blob.content.decode('utf-8').split('\n')

    for line in lines:
        if line.startswith('tree'):
            tree_hash = line.split()[1]
        elif line.startswith('parent'):
            parents.append(line.split()[1])
        elif line.startswith('author'):
            author = ' '.join(line.split(' ')[1:])
        elif line.startswith('committer'):
            committer = ' '.join(line.split(' ')[1:])
        elif line == '':
            message = '\n'.join(lines[lines.index(line) + 1:]).rstrip()
            break

    return Commit(tree_hash=tree_hash, parents=parents, author=author, committer=committer, message=message)


def parse_tree(blobs: dict[str, Blob], tree_root: Blob, ignore_missing: bool = True) -> Tree:
    """
    Parse tree blob
    :param blobs: all read blobs (by traverse_objects)
    :param tree_root: tree blob to parse
    :param ignore_missing: ignore blobs which were not found in objects directory
    :return: tree contains children blobs (or only part of them found in objects directory)
    NB. Children blobs are not being parsed according to type.
        Also nested tree blobs are not being traversed.
    """
    assert tree_root.type_ == BlobType.TREE
    entries = {}
    idx = 0
    content = tree_root.content

    while idx < len(content):
        mode_end = content.find(b' ', idx)
        name_end = content.find(b'\x00', mode_end)
        name = content[mode_end + 1:name_end].decode('utf-8')
        sha1 = content[name_end + 1:name_end + 21].hex()

        if sha1 in blobs:
            entries[name] = blobs[sha1]
        elif not ignore_missing:
            assert False, f'Missing blob {sha1} for {name}'

        idx = name_end + 21

    return Tree(children=entries)


def find_initial_commit(blobs: dict[str, Blob]) -> Commit:
    """
    Iterate over blobs and find initial commit (without parents)
    :param blobs: blobs read from objects dir
    :return: initial commit
    """
    for blob_hash, blob in blobs.items():
        if blob.type_ == BlobType.COMMIT:
            commit = parse_commit(blob)
            if len(commit.parents) == 0:
                return commit

    raise ValueError("Initial commit not found")


def search_file(blobs: dict[str, Blob], tree_root: Blob, filename: str) -> Blob:
    """
    Traverse tree blob (can have nested tree blobs) and find requested file,
    check if file was not found (assertion).
    :param blobs: blobs read from objects dir
    :param tree_root: root blob for traversal
    :param filename: requested file
    :return: requested file blob
    """
    tree = parse_tree(blobs, tree_root)

    if filename in tree.children:
        return tree.children[filename]

    for name, blob in tree.children.items():
        if blob.type_ == BlobType.TREE:
            result = search_file(blobs, blob, filename)
            if result:
                return result

    raise FileNotFoundError(f'File {filename} not found in the tree')
