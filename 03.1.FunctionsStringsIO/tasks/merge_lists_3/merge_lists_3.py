import typing as tp
import heapq


def merge(input_streams: tp.Sequence[tp.IO[bytes]], output_stream: tp.IO[bytes]) -> None:
    """
    Merge input_streams in output_stream
    :param input_streams: list of input streams. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :param output_stream: output stream. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :return: None
    """
    min_heap = []

    for i, stream in enumerate(input_streams):
        line = stream.readline()
        if line:
            min_heap.append((int(line.strip()), i, line))

    heapq.heapify(min_heap)

    while min_heap:
        val, stream_index, original_line = heapq.heappop(min_heap)
        output_stream.write(original_line)
        next_line = input_streams[stream_index].readline()
        if next_line:
            heapq.heappush(min_heap, (int(next_line.strip()), stream_index, next_line))
