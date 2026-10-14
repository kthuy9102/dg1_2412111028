import json
import os
import uuid

from flask import Flask, jsonify, render_template_string, request

STUDENT_FILE = os.path.join("app", "data", "students.json")
REQUIRED_FIELDS = {"ho_ten", "lop", "diem"}

app = Flask(__name__)


def read_students():
    if not os.path.exists(STUDENT_FILE):
        return []

    with open(STUDENT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    return data if isinstance(data, list) else []


def write_students(students):
    os.makedirs(os.path.dirname(STUDENT_FILE), exist_ok=True)

    with open(STUDENT_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)


PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>DG1 – <Họ tên> – <MSSV></title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <main>
        <h1>DG1 – <Họ tên> – <MSSV></h1>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm</th>
                </tr>
            </thead>
            <tbody>
                {% for s in students %}
                <tr>
                    <td>{{ s.id }}</td>
                    <td>{{ s.ho_ten }}</td>
                    <td>{{ s.lop }}</td>
                    <td>{{ s.diem }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </main>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE, students=read_students())


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "student": "<MSSV>"})


@app.get("/api/students")
def get_students():
    students = read_students()
    lop = request.args.get("lop")

    if lop:
        students = [s for s in students if str(s.get("lop", "")).lower() == lop.lower()]

    return jsonify(students)


@app.get("/api/students/<student_id>")
def get_student(student_id):
    for student in read_students():
        if str(student.get("id")) == student_id:
            return jsonify(student)

    return jsonify({"error": "Student not found"}), 404


@app.post("/api/students")
def create_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(sorted(missing))}"}), 400

    try:
        diem = float(data["diem"])
    except (TypeError, ValueError):
        return jsonify({"error": "diem must be a number between 0 and 10"}), 400

    if not 0 <= diem <= 10:
        return jsonify({"error": "diem must be between 0 and 10"}), 400

    student = {
        "id": str(uuid.uuid4()),
        "ho_ten": str(data["ho_ten"]).strip(),
        "lop": str(data["lop"]).strip(),
        "diem": diem,
    }

    students = read_students()
    students.append(student)
    write_students(students)

    return jsonify(student), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
