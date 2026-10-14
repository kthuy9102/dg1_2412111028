from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'students.json')

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Loi doc file json: {e}")
        return []

def write_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Câu C1: GET / - Trả về trang HTML danh sách sinh viên
@app.route('/')
def index():
    students = read_data()
    return render_template('index.html', students=students)

# Câu C2: các REST API GET
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "student": "2412111028"})

@app.route('/api/students', methods=['GET'])
def get_students():
    students = read_data()
    lop = request.args.get('lop')
    if lop:
        students = [s for s in students if s.get('lop') == lop]
    return jsonify(students)

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    students = read_data()
    student = next((s for s in students if s['id'] == student_id), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student)

# Câu C3: POST /api/students - Thêm sinh viên mới
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request"}), 400

    required_fields = ['mssv', 'ho_ten', 'lop', 'diem']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field {field}"}), 400

    try:
        diem = float(data['diem'])
        if diem < 0 or diem > 10:
            return jsonify({"error": "Diem must be between 0 and 10"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid diem"}), 400

    students = read_data()
    new_id = max([s['id'] for s in students], default=0) + 1
    new_student = {
        "id": new_id,
        "mssv": str(data['mssv']),
        "ho_ten": str(data['ho_ten']),
        "lop": str(data['lop']),
        "diem": diem
    }
    students.append(new_student)
    write_data(students)
    return jsonify(new_student), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
