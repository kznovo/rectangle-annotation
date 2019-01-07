import csv
from pathlib import Path


class CSVLabelHandler:
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        rowheader = ["filename", "obj_name", "xmin", "ymin", "xmax", "ymax"]

        if not self.csv_path.is_file():
            with open(self.csv_path, "w") as f:
                writer = csv.writer(f)
                writer.writerow(self.rowheader)

        with open(self.csv_path, "r") as f:
            reader = csv.reader(f)
            self.header = next(reader)
            self.csv_contents = list(reader)
            self.filename_idx = self.header.index("filename")
            self.column_sort_wrong2right = [
                self.header.index(column) for column in rowheader
            ]
            self.column_sort_right2wrong = [
                rowheader.index(column) for column in self.header
            ]

    def labels_out(self, filename):
        out_labels = []
        for row in self.csv_contents:
            if row[self.filename_idx] == filename:
                row = [row[i] for i in self.column_sort_wrong2right]
                out_labels.append(row)
        return out_labels

    def overwrite(self, filename, in_labels):
        with open(self.csv_path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.header)

            for row in self.csv_contents:
                if row[self.filename_idx] != filename:
                    writer.writerow(row)

            for label in in_labels:
                label = [label[i] for i in self.column_sort_right2wrong]
                writer.writerow(label)
