# Vary หาค่าคะแนนที่สูงที่สุด

- ค่าคะแนน เกิดจาก Score = Weight * (ความถี่ของปัจจัยเฉพาะ/ความถี่รวมของปัจจัย)
- ค่าคะแนนรวม = Summation(score)

ฉะนั้น ถ้าอยากหาคะแนนที่สูงที่สุด ปัจจัยที่เรามองหาได้ คือ (ความถี่ของปัจจัยเฉพาะ/ความถี่รวมของปัจจัย)
ทีนี้การหาสร้างต้นไม้ตัดสินใจ (เพื่อหาคะแนนรวม) เป็นฟังก์ชันของ

```
=> generate_decision_tree(factors, weights, hotel_name, rule_year, rule_month)
```

สิ่งที่ต้อง vary คือ factors ในขณะที่ weights จะเปลี่ยนไปตามขนาดของ factors เช่น 2 factors ก็จะมีค่า `weights = [50, 50]` แต่ถ้าเป็น 4 factors ก็จะเป็น `weights = [25, 25, 25, 25]` และ output ที่ต้องการคือต้นไม้ตัดสินใจที่มีคะแนนรวมของแต่ละสายของต้นไม้
เช่น

```
factors = ["stay", "length_of_stay", "review_group"], hotel_name = "Amari Phuket"
```

เราจะได้ตารางผลลัพธ์ประมาณนี้ - **(1) ตารางผลลัพธ์ของการหาคะแนนในทุกปัจจัย**

```
Outcome, Factor1, Factor2, Factor3, Score
1, stay:DEC-FEB, length_of_stay:1-7, review_group:solo, 48%
2, stay:MAR-MAY, length_of_stay:1-7, review_group:solo, 35%
...
n, stay:SEP-NOV, length_of_stay:>15, review_group:Family, 10%
```

ซึ่งลำดับของ Factor จริง ๆ แล้วก็มีความสำคัญ เนื่องจากจะทำให้การสร้างกฏเจอว่ามีความสัมพันธ์ดังกล่าวจริงหรือไม่ ดังนั้น Input เพื่อสร้าง decision tree จึงจะต้อง vary ค่าของ factor ด้วย - **(2) การสลับตำแหน่งของ Factor**

```
รอบที่ 1: factors = ["stay", "length_of_stay", "review_group"]
รอบที่ 2: factors = ["stay", "review_group", "length_of_stay"]
รอบที่ 3: factors = ["length_of_stay", "stay", "review_group"]
รอบที่ 4: factors = ["length_of_stay", "review_group", "stay"]
รอบที่ 5: factors = ["review_group", "stay", "length_of_stay"]
รอบที่ 6: factors = ["review_group", "length_of_stay", "stay"]
```

และในขณะเดียวกัน จำนวนของ factors ก็จำเป็นด้วย โดยจะต้องเริ่มทำงานตั้งแต่ 1 factors ไปจนถึง 5 factors ที่รองรับ และจะต้องสลับลำดับกันด้วย โดยปัจจัย 5 ปัจจัย ได้แก่ `["stay", "length_of_stay", "country", "review_group", "room_type"]` - **(3) ปัจจัยที่รองรับทั้งหมด** โดยค่ากรณีที่ได้จากการเลือกเฉพาะปัจจัย (ไม่มีการสลับตำแหน่งของปัจจัยที่เลือก) (คิดแบบ Permutation: nPr) จะทำได้ดังนี้ - **(4) การเลือกปัจจัยตั้งแต่ 1-5 ปัจจัย**

- **1 ปัจจัย** = 5 กรณี
- **2 ปัจจัย** = 20 กรณี
- **3 ปัจจัย** = 60 กรณี
- **4 ปัจจัย** = 120 กรณี
- **5 ปัจจัย** = 120 กรณี

ซึ่งฟังก์ชันที่จะสร้างใหม่ เป็นการต่อยอดจากการสร้างต้นไม้ โดยมีระเบียบวิธีการทำงานดังนี้

- หาปัจจัยที่รองรับทั้งหมด **Ref: (3)**
- นำปัจจัยที่รองรับทั้งหมด มาหยิบเลือกตั้งแต่ 1-5 ปัจจัย **Ref: (4)** --> *list_1*
- นำปัจจัยถูกหยิบเลือกแล้ว มาสลับตำแหน่งและบันทึกไว้ **Ref: (2)** --> *list_2*
- สร้างต้นไม้ตัดสินใจในทุกกรณีตาม *list_2* --> *cummulative_result_score_table*
  - สร้างค่า weights ที่สอดคล้องกับจำนวนของ factors 
  - เรียกฟังก์ชันสร้างต้นไม้การตัดสินใจ ได้ผลลัพธ์เป็น --> *result_decision_tree* 
  - สกัดค่าจาก *result_decision_tree* ออกมาเป็นค่าคะแนนตามรูปแบบตาราง **Ref: (1)** --> *result_score_table*
  - นำผลลัพธ์ที่ได้จาก *result_score_table* มาเติมในตารางลัพธ์ --> *cummulative_result_score_table*

ผลลัพธ์ของฟังก์ชันจะได้เป็นตารางในรูปแบบตามตารางที่ (1) ซึ่งสามารถนำมาเรียงค่าหาคะแนนที่สูงที่สุดได้