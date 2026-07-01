import os
import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

COURSE_SERVICE_URL = os.environ.get("COURSE_SERVICE_URL", "http://localhost:5001")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://localhost:5002")

@app.route("/api/courses/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/courses/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_course(path):
    target_url = f"{COURSE_SERVICE_URL}/api/courses/{path}"
    if request.query_string:
        target_url = f"{target_url}?{request.query_string.decode('utf-8')}"
    return forward_request(target_url)

@app.route("/api/students/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/students/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_student(path):
    target_url = f"{STUDENT_SERVICE_URL}/api/students/{path}"
    if request.query_string:
        target_url = f"{target_url}?{request.query_string.decode('utf-8')}"
    return forward_request(target_url)

@app.route("/api/departments/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/departments/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_department(path):
    target_url = f"{COURSE_SERVICE_URL}/api/departments/{path}"
    if request.query_string:
        target_url = f"{target_url}?{request.query_string.decode('utf-8')}"
    return forward_request(target_url)

def forward_request(url):
    try:
        # Exclude Host header so target server doesn't get confused
        headers = {k: v for k, v in request.headers if k.lower() != 'host'}
        
        # Forward request to downstream microservice
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )
        
        # Filter out hop-by-hop headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Target microservice is down / unreachable"}), 503
    except Exception as e:
        return jsonify({"error": f"Gateway error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
