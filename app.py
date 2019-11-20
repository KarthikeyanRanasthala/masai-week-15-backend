from flask import Flask, request, jsonify
from flask_cors import CORS

import csv

app = Flask(__name__)
CORS(app)


def get_uid():
    lst = read_csv()
    if len(lst) == 0:
        return 1
    return int(lst[len(lst) - 1]["uid"]) + 1


def single_filter(lst, filter_type, value):
    filtered_lst = []
    for item in lst:
        if item[filter_type] == value:
            filtered_lst.append(item)
    return filtered_lst


def multi_filter(lst, filter_one, value_one, filter_two, value_two):
    filtered_lst = []
    for item in lst:
        if item[filter_one] == value_one and item[filter_two] == value_two:
            filtered_lst.append(item)
    return filtered_lst


def read_csv(grade=None, section=None, exam_type=None):
    lst = []
    filtered_lst = []
    with open("students_marks.csv") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            lst.append(row)
        if grade == None and section == None and exam_type == None:
            return lst
        else:
            if not grade == None and not section == None and not exam_type == None:
                for item in lst:
                    if (
                        item["grade"] == str(grade)
                        and item["section"] == section
                        and item["exam_type"] == exam_type
                    ):
                        filtered_lst.append(item)
                return filtered_lst
            elif not grade == None and not section == None:
                return multi_filter(lst, "grade", str(grade), "section", section)
            elif not grade == None and not exam_type == None:
                return multi_filter(lst, "grade", str(grade), "exam_type", exam_type)
            elif not exam_type == None and not section == None:
                return multi_filter(lst, "exam_type", exam_type, "section", section)
            elif not grade == None:
                return single_filter(lst, "grade", str(grade))
            elif not section == None:
                return single_filter(lst, "section", section)
            else:
                return single_filter(lst, "exam_type", exam_type)


def write_csv(
    name,
    grade,
    section,
    exam_type,
    english,
    hindi,
    maths,
    science,
    social,
    open_type="a",
    current_uid=1,
    operation="edit",
):
    lst = read_csv()
    if not operation == "Delete":
        percentage = ((english + hindi + maths + science + social) / 500) * 100
        percentage = round(percentage, 2)
        uid = get_uid()
        if percentage >= 85:
            performance = "Excellent"
        elif percentage < 85 and percentage >= 75:
            performance = "Very Good"
        elif percentage < 75 and percentage >= 60:
            performance = "Good"
        else:
            performance = "Needs To Improve"
    with open("students_marks.csv", open_type) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "uid",
                "name",
                "grade",
                "section",
                "exam_type",
                "english",
                "hindi",
                "maths",
                "science",
                "social",
                "performance",
                "percentage",
            ],
        )
        if open_type == "a":
            writer.writerow(
                {
                    "uid": uid,
                    "name": name,
                    "grade": grade,
                    "section": section,
                    "exam_type": exam_type,
                    "english": english,
                    "hindi": hindi,
                    "maths": maths,
                    "science": science,
                    "social": social,
                    "performance": performance,
                    "percentage": percentage,
                }
            )
            return {"uid": uid, "percentage": percentage, "performance": performance}
        elif operation == "edit":
            new_lst = []
            for item in lst:
                if item["uid"] == current_uid:
                    new_lst.append(
                        {
                            "uid": current_uid,
                            "name": name,
                            "grade": grade,
                            "section": section,
                            "exam_type": exam_type,
                            "english": english,
                            "hindi": hindi,
                            "maths": maths,
                            "science": science,
                            "social": social,
                            "performance": performance,
                            "percentage": percentage,
                        }
                    )
                else:
                    new_lst.append(item)
            writer.writeheader()
            for item in new_lst:
                writer.writerow(item)
            return {
                "uid": current_uid,
                "percentage": percentage,
                "performance": performance,
            }
        else:
            print(current_uid)
            new_lst = []
            for item in lst:
                if not item["uid"] == str(current_uid):
                    new_lst.append(item)
            writer.writeheader()
            for item in new_lst:
                writer.writerow(item)
            return {"uid": current_uid, "message": "Deleted"}


@app.route("/", methods=["GET", "POST", "PUT", "DELETE"])
def get_details():
    if request.method == "POST":
        message = write_csv(
            request.json["name"],
            request.json["grade"],
            request.json["section"],
            request.json["exam_type"],
            int(request.json["english"]),
            int(request.json["hindi"]),
            int(request.json["maths"]),
            int(request.json["science"]),
            int(request.json["social"]),
        )
        return jsonify({"msg": message})
    elif request.method == "PUT":
        message = write_csv(
            request.json["name"],
            request.json["grade"],
            request.json["section"],
            request.json["exam_type"],
            int(request.json["english"]),
            int(request.json["hindi"]),
            int(request.json["maths"]),
            int(request.json["science"]),
            int(request.json["social"]),
            "w",
            str(request.json["uid"]),
        )
        return jsonify(message)
    elif request.method == "DELETE":
        uid = request.args.get("id", default=1, type=int)
        print(uid)
        response = write_csv(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "w",
            str(uid),
            "Delete",
        )
        return jsonify(response)
    else:
        grade = request.args.get("grade", default=None, type=int)
        section = request.args.get("section", default=None, type=str)
        exam_type = request.args.get("exam_type", default=None, type=str)
        return jsonify({"data": read_csv(grade, section, exam_type)})


@app.route("/user/<int:uid>")
def get_user(uid):
    lst = read_csv()
    new_list = []
    for item in lst:
        if item["uid"] == str(uid):
            new_list.append(item)
            break
    return jsonify({"data": new_list[0]})


if __name__ == "__main__":
    app.run()
