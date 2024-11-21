# 프로그램 창
![image](https://github.com/user-attachments/assets/46db32ca-0b16-43d6-b775-c4ddbbe9b5c1)<br>
|기능|내용|
|------|---|
|LaserOn|레이저 센서 켜기<br> b'\xAA\x00\x01\xBE\x00\x01\x00\x01\xC1' 명령어 전송|
|LaserOff|레이저 센서 끄기<br> b'\xAA\x00\x01\xBE\x00\x01\x00\x00\xC0' 명령어 전송|
|CntinusAuto|레이저 센서 연속 측정 <br> b'\xAA\x00\x00\x20\x00\x01\x00\x04\x25' 명령어 전송|
|Stop|측정 정지 <br> b'\x58' 명령어 전송|
|Save|Excel 파일로 데이터 저장|
|Clear|초기화|
# 프로그램 실행화면
![image](https://github.com/user-attachments/assets/c56b620a-0e3b-40bf-a657-c29d1abcef5b)
