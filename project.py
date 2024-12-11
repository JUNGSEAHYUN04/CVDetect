import cv2
from ultralytics import YOLO
import pyttsx3
import threading
import queue
import numpy as np
import speech_recognition as sr
import time
import logging

# YOLO 디버그 출력 숨기기
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# YOLO 모델 로드
model = YOLO("yolo11n.pt")

# 음성 엔진 초기화
engine = pyttsx3.init()
engine.setProperty("rate", 200)
engine.setProperty("volume", 1.0)

# 음성 출력 큐 생성
speech_queue = queue.Queue(maxsize=5)

# 웹캠 비디오 캡처 시작
cap = cv2.VideoCapture(0)

# 탐지 제한 클래스 및 상태
selected_class = None
announced_objects = {}
run_program = True  # 프로그램 실행 상태
class_announcement_time = {}  # 클래스별 "많음" 메시지 중복 방지
tracked_objects = {}  # 특정 객체의 추적 정보

# 신호등 클래스 ID 및 신호 기준 설정
TRAFFIC_LIGHT_CLASS_ID = 9  # 신호등 클래스 ID
GREEN_LIGHT_THRESHOLD = 0.5  # 초록불 신뢰도 기준
RED_LIGHT_THRESHOLD = 0.5    # 빨간불 신뢰도 기준

# 신호등 음성 안내 기록
last_traffic_light_state = None  # 마지막 안내된 신호등 상태

# 음성 출력 스레드 함수
def speech_worker():
    last_message = None
    while True:
        try:
            message = speech_queue.get()
            if message == "STOP":  # 종료 신호
                break
            if message != last_message:  # 중복 메시지 방지
                engine.say(message)
                engine.runAndWait()
                last_message = message
        except queue.Empty:
            pass

# 음성 명령 스레드 함수
def voice_command_worker():
    global selected_class, run_program
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=5)
        print("------명령인식중-------")

        while True:
            try:
                print("(대기중)")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio, language="ko-KR")
                print(f"명령 인식: {command}")

                if "사람" in command or "person" in command:
                    selected_class = "person"
                    speech_queue.put("사람 감지 모드")
                elif "모든 탐지" in command:
                    selected_class = None
                    speech_queue.put("일반 감지 모드")
                elif "종료" in command:
                    run_program = False
                    speech_queue.put("종료")
                elif "시작" in command:
                    run_program = True
                    speech_queue.put("시작")

                elif "신호등" in command:
                    speech_queue.put("신호등 감지 모드")
                    selected_class = "traffic light"  

                # "차량" 명령을 인식하면 차량 감지
                elif "차량" in command:
                    speech_queue.put("차량 감지 모드")
                    selected_class = "car"  # 차량만 감지하도록 설정
                elif "버스" in command:  # "bus"를 추가하여 버스를 감지하도록 설정
                    speech_queue.put("버스 감지 모드")
                    selected_class = "bus"  
                elif "트럭" in command:  # "truck"을 추가하여 트럭을 감지하도록 설정
                    speech_queue.put("트럭 감지 모드")
                    selected_class = "truck"  

                else:
                    print("명령어 이해 안됨")
            except sr.UnknownValueError:
                print("음성을 이해못함")
            except sr.RequestError as e:
                print(f"구글 스피치 서비스 오류: {e}")

# 음성 출력 스레드 시작
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

# 음성 명령 스레드 시작
voice_thread = threading.Thread(target=voice_command_worker, daemon=True)
voice_thread.start()

# 메인 루프
while True:
    if not run_program:
        time.sleep(1)
        continue

    ret, frame = cap.read()
    if not ret:
        print("웹캠을 열 수 없습니다.")
        break

    frame_height, frame_width, _ = frame.shape
    frame_center = np.array([frame_width // 2, frame_height // 2])

    results = model(frame)
    object_counts = {}  # 클래스별 객체 개수 저장

    for obj in results[0].boxes.data.tolist():
        confidence = obj[4]
        if confidence >= 0.5:
            class_id = int(obj[5])
            class_name = model.names[class_id]

            if selected_class is not None and class_name != selected_class:
                continue

            # 객체 위치 추적
            x1, y1, x2, y2 = map(int, obj[:4])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            center_coords = np.array([center_x, center_y])
            distance = np.linalg.norm(center_coords - frame_center)

            # 객체 추적
            if class_name not in tracked_objects:
                tracked_objects[class_name] = {'lost': False, 'last_seen': time.time()}
            else:
                tracked_objects[class_name]['last_seen'] = time.time()
                tracked_objects[class_name]['lost'] = False

            # 새로운 객체 안내 (5초 이내 중복 안내 방지)
            current_time = time.time()
            if class_name not in announced_objects or current_time - announced_objects[class_name] > 5:
                if not speech_queue.full():
                    speech_queue.put(class_name)
                announced_objects[class_name] = current_time

            # 위험 감지 및 UI 설정
            if distance < 20:
                speech_queue.queue.clear()  # 기존 음성 명령을 초기화
                speech_queue.put(f"{class_name}위험")
                color = (0, 255, 255)  # 노란색 (위험 경고)
                thickness = 4  # 두꺼운 박스 (위험 강조)

                # 화면 중앙에 위험 표시
                cv2.putText(frame, "Danger", (frame.shape[1] // 2 - 50, frame.shape[0] // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            else:
                color = (0, 255, 0)  # 초록색 (안전)
                thickness = 2  # 얇은 박스 (안전)

            # 바운딩 박스 그리기
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # 객체 이름 표시
            cv2.putText(frame, f"{class_name}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 신호등 감지 및 음성 안내
    for obj in results[0].boxes.data.tolist():
        confidence = obj[4]
        if confidence >= 0.5:
            class_id = int(obj[5])
            if class_id == TRAFFIC_LIGHT_CLASS_ID:  # 신호등이 탐지된 경우
                x1, y1, x2, y2 = map(int, obj[:4])
                traffic_light_roi = frame[y1:y2, x1:x2]

                hsv = cv2.cvtColor(traffic_light_roi, cv2.COLOR_BGR2HSV)

                # 신호등 색상 범위 설정 (초록, 빨강)
                blue_lower = np.array([100, 50, 50])  # 초록색 하한
                blue_upper = np.array([140, 255, 255])  # 초록색 상한
                red_lower1 = np.array([0, 50, 50])  # 빨간색 하한
                red_upper1 = np.array([10, 255, 255])  # 빨간색 상한

                blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
                red_mask = cv2.inRange(hsv, red_lower1, red_upper1)

                blue_ratio = np.sum(blue_mask > 0) / blue_mask.size
                red_ratio = np.sum(red_mask > 0) / red_mask.size

                # 초록불/빨간불 판단
                if blue_ratio > 0.1:
                    speech_queue.put("파란불 입니다")
                    last_traffic_light_state = "green"
                elif red_ratio > 0.1:
                    speech_queue.put("빨간불 입니다")
                    last_traffic_light_state = "red"

    # 화면에서 벗어난 객체 추적
    for class_name, data in tracked_objects.items():
        if time.time() - data['last_seen'] > 2 and not data['lost']:
            speech_queue.put(f"{class_name} 사라짐")
            tracked_objects[class_name]['lost'] = True

    cv2.imshow("Project", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        speech_queue.put("STOP")
        break

cap.release()
cv2.destroyAllWindows()
