from PIL import Image
import struct

import os
SAMPLES = os.getenv("SAMPLES_DIR") or error("set SAMPLES_DIR")
SEL = {
 "Q00_credits":  ("QEqpZw-BKipORhHHWGGfPzErWDOHK6DNKYXw4JRNgfk", "00.jpg"),
 "Q01_spread":   ("QEqpZw-BKipORhHHWGGfPzErWDOHK6DNKYXw4JRNgfk", "01.jpg"),
 "Q10_regular":  ("QEqpZw-BKipORhHHWGGfPzErWDOHK6DNKYXw4JRNgfk", "10.jpg"),
 "Q22_regular":  ("QEqpZw-BKipORhHHWGGfPzErWDOHK6DNKYXw4JRNgfk", "22.jpg"),
 "V01_square":   ("Vt2Mi9QUvwiWlJqM3NKk1regsF8upkyPvSsq-rDniKk", "01.jpg"),
 "V08_regular":  ("Vt2Mi9QUvwiWlJqM3NKk1regsF8upkyPvSsq-rDniKk", "08.jpg"),
 "V14_regular":  ("Vt2Mi9QUvwiWlJqM3NKk1regsF8upkyPvSsq-rDniKk", "14.jpg"),
 "I12_regular":  ("iEystyKWjCcPCCsLKopZ57brJhc1SBJO3Yr9jUYAl5g", "12.jpg"),
}
for name,(ch,fn) in SEL.items():
    im = Image.open(os.path.join(SAMPLES, ch, fn)).convert("L")
    im.save(os.path.join("pages", name + ".png"))
    with open(os.path.join("raw", name + ".gray"), "wb") as f:
        f.write(struct.pack("<II", im.width, im.height))
        f.write(im.tobytes())
    print(name, im.size)
