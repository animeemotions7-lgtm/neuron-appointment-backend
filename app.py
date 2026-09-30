from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Doctor schedules
DOCTORS = {
    "Dr. Anjit Kumar": {
        "speciality": "Orthopedics",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "start": 10,
        "end": 14
    },
    "Dr. Jyoti": {
        "speciality": "Gynecology",
        "days": ["Monday", "Wednesday", "Saturday"],
        "start": 11,
        "end": 15
    }
}


def get_tool_call(data):
    message = data.get("message", {})

    tool_calls = message.get("toolCallList", [])

    if not tool_calls:
        tool_calls = message.get("toolWithToolCallList", [])

    if not tool_calls:
        return None

    return tool_calls[0]


def get_arguments(tool_call):
    function = tool_call.get("function", {})
    arguments = function.get("arguments", {})

    if isinstance(arguments, str):
        import json
        try:
            arguments = json.loads(arguments)
        except:
            arguments = {}

    if not arguments:
        tool_call_data = tool_call.get("toolCall", {})
        arguments = tool_call_data.get("parameters", {})

    return arguments


@app.route("/check-appointment", methods=["POST"])
def check_appointment():
    data = request.get_json(silent=True) or {}

    tool_call = get_tool_call(data)

    if not tool_call:
        return jsonify({"results": []}), 200

    tool_call_id = (
        tool_call.get("id")
        or tool_call.get("toolCall", {}).get("id")
    )

    arguments = get_arguments(tool_call)

    doctor = arguments.get("doctor_name")
    speciality = arguments.get("speciality")
    date = arguments.get("date")

    if not date:
        result = {
            "available": False,
            "message": "Please provide the appointment date."
        }

    else:
        try:
            appointment_date = datetime.strptime(date, "%Y-%m-%d")
            day_name = appointment_date.strftime("%A")

            doctor_info = None

            if doctor in DOCTORS:
                doctor_info = DOCTORS[doctor]

            else:
                for name, info in DOCTORS.items():
                    if info["speciality"].lower() == str(speciality).lower():
                        doctor = name
                        doctor_info = info
                        break

            if not doctor_info:
                result = {
                    "available": False,
                    "message": "No matching doctor was found."
                }

            elif day_name not in doctor_info["days"]:
                result = {
                    "available": False,
                    "doctor": doctor,
                    "speciality": doctor_info["speciality"],
                    "date": date,
                    "message": f"{doctor} is not available on {day_name}."
                }

            else:
                slots = []

                for hour in range(
                    doctor_info["start"],
                    doctor_info["end"]
                ):
                    suffix = "AM" if hour < 12 else "PM"
                    display_hour = hour if hour <= 12 else hour - 12
                    slots.append(f"{display_hour}:00 {suffix}")

                result = {
                    "available": True,
                    "doctor": doctor,
                    "speciality": doctor_info["speciality"],
                    "date": date,
                    "day": day_name,
                    "available_slots": slots
                }

        except ValueError:
            result = {
                "available": False,
                "message": "Invalid date. Please use YYYY-MM-DD."
            }

    return jsonify({
        "results": [
            {
                "toolCallId": tool_call_id,
                "result": str(result)
            }
        ]
    }), 200


@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    data = request.get_json(silent=True) or {}

    tool_call = get_tool_call(data)

    if not tool_call:
        return jsonify({"results": []}), 200

    tool_call_id = (
        tool_call.get("id")
        or tool_call.get("toolCall", {}).get("id")
    )

    arguments = get_arguments(tool_call)

    patient_name = arguments.get("patient_name")
    age = arguments.get("age")
    gender = arguments.get("gender")
    phone = arguments.get("phone")
    email = arguments.get("email")
    doctor = arguments.get("doctor_name")
    speciality = arguments.get("speciality")
    appointment_date = arguments.get("appointment_date")
    appointment_time = arguments.get("appointment_time")
    notes = arguments.get("notes")

    # Basic validation
    required_fields = [
        patient_name,
        age,
        gender,
        phone,
        doctor,
        speciality,
        appointment_date,
        appointment_time
    ]

    if not all(required_fields):
        result = {
            "success": False,
            "message": "Required appointment information is missing."
        }

    elif doctor not in DOCTORS:
        result = {
            "success": False,
            "message": "The selected doctor was not found."
        }

    else:
        appointment_id = (
            "FW-"
            + str(appointment_date).replace("-", "")
            + "-"
            + str(appointment_time).replace(":", "").replace(" ", "")
        )

        result = {
            "success": True,
            "appointment_id": appointment_id,
            "patient_name": patient_name,
            "age": age,
            "gender": gender,
            "phone": phone,
            "email": email,
            "doctor": doctor,
            "speciality": speciality,
            "date": appointment_date,
            "time": appointment_time,
            "notes": notes,
            "message": "Appointment booking request accepted."
        }

    return jsonify({
        "results": [
            {
                "toolCallId": tool_call_id,
                "result": str(result)
            }
        ]
    }), 200


@app.route("/", methods=["GET"])
def home():
    return "Fit Well Hospital appointment backend is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)