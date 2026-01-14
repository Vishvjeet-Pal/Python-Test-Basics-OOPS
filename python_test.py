# Generated from python_test.ipynb
# Sections and markdown converted to comments.

# Section B
# Python script that reads data from log file and store in appropriate data structure
logs = []
try:
    with open("log.txt", 'r') as file:
        for line in file:
            log = line.split("\t", 3)[:3]
            if len(log) < 3:
                continue
            level, date, source = log
            log = {"level": level, "date": date, "source": source}
            logs.append(log)
except FileNotFoundError:
    logs = []

# Keep mapping for severity levels
level_mapping = {
    "Information": 1,
    "Warning": 2,
    "Error": 4,
    "Critical": 8,
}

# Create mask for Error and Critical
mask = level_mapping["Error"] | level_mapping["Critical"]  # using bitwise OR operator

filtered_logs = []
for log in logs:
    if level_mapping.get(log["level"], 0) & mask:  # using bitwise AND
        filtered_logs.append(log)
print(filtered_logs)


# Section C - Move the upper logic to functions
def read_log(filepath):
    logs = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                log = line.split("\t", 3)[:3]
                if len(log) < 3:
                    continue
                level, date, source = log
                log = {"level": level, "date": date, "source": source}
                logs.append(log)
        return logs
    except FileNotFoundError:
        print(f"{filepath} not found at specified path")
        return []


def filter_logs(logs):
    filtered_logs = []
    for log in logs:
        if level_mapping.get(log["level"], 0) & mask:
            filtered_logs.append(log)
    return filtered_logs


if __name__ == "__main__":
    logs = read_log("log.txt")
    filtered_logs = filter_logs(logs)
    print(filtered_logs)

    # Writing to file
    try:
        with open("log_created", "a") as file:
            for log in filtered_logs:
                file.write(f"{log['level']} {log['date']} {log['source']}")
            print("File created successfully")
    except Exception as e:
        print(f"Unexpected error occured {e}")


# Section D - Create LogFile class
from abc import ABC, abstractmethod
from collections import Counter


class Logfile(ABC):
    def __init__(self, filepath):
        self.filepath = filepath
        self.records = []

    def load_file(self):
        self.records = []
        with open(self.filepath, "r") as file:
            for line in file:
                parsed = self.parse_record(line.strip())
                if parsed:
                    self.records.append(parsed)

    def add_record(self, raw_record):
        parsed = self.parse_record(raw_record)
        if not parsed:
            raise ValueError("Invalid record format")
        with open(self.filepath, "a") as file:
            file.write(raw_record + "\n")
        # self.records.append(parsed)

    @abstractmethod
    def parse_record(self, record):
        pass

    def __len__(self):
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def __str__(self):
        return f"{self.__class__.__name__}({len(self)} records)"


# Create class UserAnalytics
import pandas as pd


class UserAnalytics(Logfile):
    def parse_record(self, record):
        parts = record.split(" ")
        if len(parts) != 2:
            raise ValueError("Invalid record format")
        user_id, action = parts
        return {"user_id": user_id, "action": action}

    def calculate_stats(self):
        user_counter = Counter()
        action_counter = Counter()

        for record in self.records:
            user_counter[record["user_id"]] += 1
            action_counter[record["action"]] += 1

        return {
            "total_records": len(self),
            "user_activity": dict(user_counter),
            "action_frequency": dict(action_counter),
        }

    def generate_report(self, filename="UserAnalytics_report.csv"):
        stats = self.calculate_stats()

        rows = [
            {"Type": "Event", "Key": record["user_id"], "Value": record["action"]}
            for record in self.records
        ]

        rows.extend(
            {"Type": "UserActivity", "Key": user, "Value": count}
            for user, count in stats["user_activity"].items()
        )

        rows.extend(
            {"Type": "ActionFrequency", "Key": action, "Value": count}
            for action, count in stats["action_frequency"].items()
        )

        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)


# Sample usage (guarded)
if __name__ == "__main__":
    analytics = UserAnalytics("user_log.txt")
    try:
        analytics.add_record("101 in")
        analytics.add_record("102 out")
        analytics.add_record("103 in")
    except Exception:
        # ignore invalid record writes during sample run
        pass
    analytics.load_file()
    analytics.generate_report()

    print(len(analytics))
    print(analytics)
    for record in analytics:
        print(record)


# Call by Reference
def square_list(ls):
    for index in range(len(ls)):
        ls[index] *= ls[index]

my_list = [1, 2, 3]
square_list(my_list)
print(my_list)  # values changed to their corresponding squares


# Copy vs Deepcopy
# Shallow Copy
import copy

num = [[1, 2], [4, 5, 6]]
shallow_copy = copy.copy(num)
print(shallow_copy)

shallow_copy[0][0] = 100  # value of original list (i.e. num) is also changed

print("num: ", num)
print("shallow_copy: ", shallow_copy)

print(num is shallow_copy)
print(num[0] is shallow_copy[0])  # nested elements have same identity


# Deep Copy
num = [[1, 2], [4, 5, 6]]
deep_copy = copy.deepcopy(num)
print(deep_copy)

deep_copy[0][0] = 100  # value of num is not changed

print("num: ", num)
print("deep_copy: ", deep_copy)

print(num is deep_copy)
print(num[0] is deep_copy[0])  # nested elements have different identity
