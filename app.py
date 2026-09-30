from flask import Flask, request, jsonify

app = Flask(__name__)


def get_tool_call(data):
    message = data.get("message", {})

    tool_calls = message.get("toolCallList", [])

    if not tool_calls:
        tool_calls = message.get("toolWithToolCallList", [])

    if not tool_calls:
        return None

    return tool_calls[0]


@app.route("/")
def home():
    return "Hospital Appointment API is running!"


@app.route("/check-appointment", methods=["POST"])
def check_appointment():
    data = request.get_json(silent=True) or {}

    tool_call = get_tool_call(data)

    if not tool_call:
        return jsonify({
            "results": []
        }), 200

    tool_call_id = tool_call.get("id") or tool_call.get("toolCall", {}).get("id")

    function = tool_call.get("function", {})
    arguments = function.get("arguments", {})

    if not arguments:
        tool_call_data = tool_call.get("toolCall", {})
        arguments = tool_call_data.get("parameters", {})

    doctor = arguments.get("doctor_name")
    speciality = arguments.get("speciality")
    date = arguments.get("date")
    preferred_time = arguments.get("preferred_time")

    result = {
        "available": True,
        "doctor": doctor or "Available doctor",
        "speciality": speciality or "",
        "date": date or "",
        "available_slots": [
            "10:00 AM",
            "11:00 AM",
            "12:30 PM"
        ]
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
        return jsonify({
            "results": []
        }), 200

    tool_call_id = tool_call.get("id") or tool_call.get("toolCall", {}).get("id")

    function = tool_call.get("function", {})
    arguments = function.get("arguments", {})

    if not arguments:
        tool_call_data = tool_call.get("toolCall", {})
        arguments = tool_call_data.get("parameters", {})

    patient_name = arguments.get("patient_name")
    doctor = arguments.get("doctor_name")
    speciality = arguments.get("speciality")
    appointment_date = arguments.get("appointment_date")
    appointment_time = arguments.get("appointment_time")

    appointment_id = (
        "NH-"
        + str(appointment_date).replace("-", "")
        + "-001"
    )

    result = {
        "success": True,
        "appointment_id": appointment_id,
        "patient_name": patient_name,
        "doctor": doctor,
        "speciality": speciality,
        "date": appointment_date,
        "time": appointment_time
    }

    return jsonify({
        "results": [
            {
                "toolCallId": tool_call_id,
                "result": str(result)
            }
        ]
    }), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)