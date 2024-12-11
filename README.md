![header](https://capsule-render.vercel.app/api?type=waving&customColorList=_hexcode=FFC0CB=200&section=header&text=Computer_Vision_Project&fontSize=45)

# 프로젝트명: 

<div align="center">
  <h1>🗣️ 시각장애인과 저시력자를 위한</h1>
  <h1>객체 탐지와 음성 인식 서비스 🕵️</h1>
</div>

<div align="center">
  <h1> MEMBER 🧑‍🤝‍🧑</h1>
  <h2>학번하고 이름 적을 공간</h2>
  ### 순서대로 적어주세요
  <h2>QB반 20231562 서예진</h2>
  <h2>QB반 20232877 심수현</h2>
  <h2>QB반 20232502 김유진</h2>


</div>

# 구현기능:

<div align="center">
<h1>Implementation Features 🤖</h1>  
<h2>처음 탐지된 객체 음성 안내📢</h2>
  ## 설명
  
<h2>신호등 음성 안내🚦</h2>

  <h3>문제상황</h3>
  <h6>비신호 횡단보도는 시각장애인에게 위험천만한 공간이다. 보행신호등도 음향신호기도 없어 차량이 다가오고 있는지를 보행자 스스로 판단해야 한다. 도로교통법에 따라 하루 중 횡단보도 통행량이 가장 많은 한 시간 동안 횡단 보행자가 150명이 넘으면 보행신호등을 설치하게 돼 있다. 비신호 횡단보도는 주로 유동인구가 적은 곳에 위치해 다른 보행자의 도움을 받기도 어렵다는 뜻이다. 3일 서울시 교통안전시설물관리시스템에 따르면 시의 관할구역 안에 보행신호등이 없는 횡단보도는 2만5509개에 달한다.(경향신문/시각장애인은 오늘도 목숨 걸고 길을 건넌다./오경민 기자)</h6>
  
  <h3>주요 코드</h3>
  <h6>객체의 클래스 id를 인식한 후 신호등 id인 경우 코드 실행 -> 
  신호등 영역을 분리하여 cvtColor를 사용하여 hsv 색상 영역을 변환 ->
  파란 비율과 빨간 비율에 따라 파란불, 빨간불 상태를 파악하여 음성으로 안내</h6>
  
  ```
  # 신호등 클래스 ID 및 신호 기준 설정
  TRAFFIC_LIGHT_CLASS_ID = 9  # 신호등 클래스 ID
  GREEN_LIGHT_THRESHOLD = 0.5  # 초록불 신뢰도 기준
  RED_LIGHT_THRESHOLD = 0.5    # 빨간불 신뢰도 기준

  # 신호등 음성 안내 기록
  last_traffic_light_state = None  # 마지막 안내된 신호등 상태

 # 객체 결과 확인
    for obj in results[0].boxes.data.tolist():
        confidence = obj[4]
        if confidence >= 0.5:
            class_id = int(obj[5])  # 클래스 id를 저장
            if class_id == TRAFFIC_LIGHT_CLASS_ID:  # 클래스 id가 신호등의 id와 같으면
                traffic_light_detected = True
                # 경계 상자 좌표 추출
                x1, y1, x2, y2 = map(int, obj[:4])  # 경계 상자 좌경
  </h6>
</div>

# 결과 

사진 첨부하면 좋을 듯
이런 분석도 한줄씩 적으면 더 좋을 듯!! 




<img src="https://capsule-render.vercel.app/api?type=waving&color_hexcode=FFC0CB=200&section=footer&fontSize=60&fontAlign=50&fontAlignY=40" height=100% width=100%>
