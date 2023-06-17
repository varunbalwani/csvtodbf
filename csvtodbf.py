import json
from datetime import date, datetime
import dbf
import csv
from tqdm import tqdm
import karvy_direct
import traceback
from uuid import uuid4

options = {
    "KARVY_DIRECT": karvy_direct.get_column_map()
}


def error_dump(file_name, error_data):
    if len(error_data) <= 0:
        return
    error_path = file_name + [f"error-{uuid4()}", "json"]
    error_path = ".".join(error_path)
    with open(error_path, "w") as fp:
        json.dump(error_data, fp)


def update_progress(percentage):
    pass

def csv_to_dbf(csv_file_path, column_map, column_list, update_progress):
    reverse_map = {value: key for key, value in column_map.items()}
    error_list = []
    result_file_path = csv_file_path.split(".")[:-1]
    dbf_file_path = result_file_path + ["dbf"]
    dbf_file_path = ".".join(dbf_file_path)
    new_table = dbf.Table(dbf_file_path, "; ".join(column_list))
    new_table.open(mode=dbf.READ_WRITE)
    with open(csv_file_path, "r") as fp:
        header = next(fp).strip().split(",")
        reader = csv.DictReader(fp, header, delimiter=",")
        data = {}
        row_list = []
        for row in tqdm(reader, position=0, desc="Reading CSV"):
            row_list.append(row)
        total = len(row_list)
        current = 0
        error_count = 0
        success_count = 0
        display_error = []
        for row in tqdm(row_list, position=1, desc="Writing to DBF"):
            current += 1
            progress = (current + 1)/total * 100
            update_progress(progress)
            try:
                for key, value in row.items():
                    dbf_key = column_map.get(key)
                    if dbf_key and value:
                        field_info = new_table.field_info(dbf_key)
                        if field_info.py_type == date:
                            value = datetime.strptime(value, "%d/%m/%Y").date()
                        data[dbf_key] = value
                new_table.append(data)
                success_count += 1
            except dbf.DbfError as e:
                error_count += 1
                error_field = ""
                if hasattr(e, "data"):
                    error_field = e.data
                traceback.print_exc()
                display_error.append(
                    {"row_no": current, "message": e.message, "csv_field": reverse_map.get(error_field),
                     "dbf_field": error_field}
                )
                error_list.append(
                    {"row_no": current, "data": row, "stack_trace": traceback.format_stack(), "message": e.message,
                     "display_error_field": reverse_map.get(error_field), "error_field": error_field,
                     "error_list": e.args}
                )
            except Exception as e:
                error_count += 1
                traceback.print_exc()
                display_error.append(
                    {"row_no": current, "message": str(e)}
                )
                error_list.append(
                    {"row_no": current, "data": row, "stack_trace": traceback.format_stack(), "message": str(e)}
                )
    new_table.close()
    error_dump(result_file_path, error_list)
    return display_error, total, success_count, error_count


# if __name__ == "__main__":
#     option_list = list(options.keys())
#     # file_path = sys.argv[1]
#     file_path = "/home/int240/PycharmProjects/csvtodbf/testdata/2023-06-14/1152027778766IA39890282.csv"
#     option = 0
# print(json.dumps(csv_to_dbf(file_path, *options.get(option_list[option]), update_progress), indent=4))