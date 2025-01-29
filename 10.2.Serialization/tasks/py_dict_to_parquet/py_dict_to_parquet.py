import pyarrow as pa
import pyarrow.parquet as pq
import typing as tp


ValueType = int | list[int] | str | dict[str, str] | None


def save_rows_to_parquet(rows: list[dict[str, ValueType]], output_filepath: str) -> None:
    """
    Save rows to parquet file.

    :param rows: list of rows containing data.
    :param output_filepath: local filepath for the resulting parquet file.
    :return: None.
    """
    map_types: dict[type, tp.Any] = {
        int: pa.int64(),
        list: pa.list_(pa.int64()),
        str: pa.string(),
        dict: pa.map_(pa.string(), pa.string())
    }

    lst_fields: list[tp.Any] = []

    current_condition: dict[str, tp.Any] = dict()
    count_keys: dict[str, int] = dict()

    for row in rows:
        for key, val in row.items():
            if key in current_condition.keys():
                if type(current_condition[key]) is not type(val):
                    raise TypeError('Field {field_name} has different types'.format(field_name=key))
                count_keys[key] += 1
                continue
            count_keys[key] = 1
            current_condition[key] = val

    for key in current_condition.keys():
        lst_fields.append(pa.field(key, map_types[type(current_condition[key])], len(rows) != count_keys[key]))
        table = pa.Table.from_pylist(rows, pa.schema(lst_fields))
        pq.write_table(table, output_filepath)
