import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('missionreport.png')

for detection in result:
    print(detection[1])
    