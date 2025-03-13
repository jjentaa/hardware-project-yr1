# กู้หนี้ ยืมสิน

## ที่มา และความสำคัญ
การสื่อสารเป็นเรื่องสำคัญ และการสื่อสารให้รู้เรื่อง ก็เป็นเรื่องที่ค่อนข้างสำคัญ
ในยุคปัจจุบันนี้ ในโลกที่มีเทคโนโลยีเต็มไปหมด ทำให้การสื่อสารซึ่งหน้าลดลง ส่งผลกระทบไปสู่ความสัมพันธ์กับผู้คนรอบตัวที่ลดลง
งานของเรา ถูกสร้างมาเพื่อแก้ปัญหานี้ นั่นคือเกมกู้ระเบิด ที่เน้นการสื่อสาร และกระชับความสัมพันธ์ 

## Background
ผู้เล่นทั้งสองฝั่งจะได้รับบทบาทให้เป็นสายลับ ที่ต้องร่วมมือกันแก้ระเบิด โดยผู้เล่นแต่ละคน จะไม่รู้วิธีแก้ระเบิดที่ตัวเองกำลังเผชิญอยู่ แต่รู้วิธีแก้ระเบิดที่ตนได้วางไว้ จึงต้องร่วมมือกันช่วยแก้ระเบิดของอีกฝ่าย

## Game Concept
- ผู้เล่นต้องช่วยกันแก้ระเบิดที่ไม่ได้อยู่กับตัวเอง ผ่านคู่มือที่ตัวเองมีให้สำเร็จ โดยผ่านการแก้ไขปริศนา ที่อาศัยความรอบคอบ รวมถึงความละเอียด
- ผู้เล่นต้องแก้ระเบิดให้เสร็จภายในเวลา 10 นาที ที่หมายความว่า ระเบิดต้องถูกแก้ทั้งสองลูกเท่านั้น และไม่มีการตอบผิดเกินกว่า 3 ครั้ง ถึงว่าจะถือว่าชนะเกมนี้

## Board Function
ใน project นี้ออกแบบให้แต่ละ board มีหน้าตาที่ต่างกัน เพื่อความหลากหลายของเกมที่ใช้เล่น รวมถึงทุกๆอุปกรณ์ที่เสริมเข้ามา จะมีการแนบไฟล์ lib ที่ใช้ร่วมกัน

### Board 1 
- Joystick `joystick.py`
- ลำโพง Buzzer `buzzer.py`
- OLED 
- LEDs 4 สี
- สวิตซ์
- 4 colours switches `fourbutton_leds.py`
- 4 digits 7 segments `tm1637.py`

### Board 2
- Joystick `joystick.py`
- ลำโพง Buzzer `buzzer.py`
- OLED
- LEDs 3 สี
- สวิตซ์ 
- Double 4 digits 7 segments with 4x4 buttons `tm1638.py`

## Dashboard
ในส่วนของ dashboard เราวางแผนให้มีทั้งหมด 2 function ใหญ่ๆ
1. การเข้าถึงคู่มือการแก้รหัสของตัวเองผ่านการกรอก secret code
2. ตัวบอกสถานะระเบิด progress bar

## Game
ในงานนี้เราได้ทำการออกแบบเกมมาทั้งหมด 6 เกม
1. `the_button.py` - ใช้ได้ทั้งสอง board
2. `morse_code.py` - ใช้ได้ทั้งสอง board
3. `maze.py` - Board2
4. `leds_memorizing.py` - Board1
5. `led_seq_v1.py` - ใช้ได้ทั้งสอง board
6. `led_seq_eiei_v1.py` - Board1

โดยเราจะรวมเกมทั้งหม และการทำ dashboard ใน `main_games.py`

## Note
- schematic ดูได้ที่ `schematic.pdf`
- flow การทำงาน `Flowchart.pdf`
