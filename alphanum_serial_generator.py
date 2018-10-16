from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
import numpy as np

# Number of Alphanumeric digits should be 4, after the 2 digit product code
# (total number of digits should be 6)

def base36_to_int(b36_num):
    # Converts base36 alphanumeric code to base 10 integer
    print(b36_num)
    converted_num = 0
    exponent = len(b36_num)-1             # Starts at the leftmost digit, the 4th digit, which is the 3rd power
    for i in range(len(b36_num)):
        if b36_num[i] == '0':
            a=0
            # do nothing
        elif ord(b36_num[i]) < 60:           # Keeping the code simple, can error out potentially
            converted_num += np.power(36, exponent)*int(b36_num[i])
        elif ord(b36_num[i]) > 63:
            converted_num += np.power(36, exponent)*(ord(b36_num[i])-65+10)

        exponent -= 1

    return converted_num

window = Tk()
window.title("Serial Number generator")

# List possible product codes, request entry
prod_code_lbl = Label(window, text="Here are the following product codes\n"
                                   "01: Transmitter\n"
                                   "03: Vibration Mote\n"
                                   "Example: 030001 \n"
                                   "\n"
                                   "Enter starting serial number (6 digits):",
                      justify=LEFT)
prod_code_lbl.grid(column=0, row=0)

# Input box for starting serial number
prod_code_txt = Text(window, height=1, width=20)
prod_code_txt.grid(column=0, row=1)

# Request number of serial numbers
num_ser_lbl = Label(window, text="\n"
                                 "Enter number of serial numbers to generate:")
num_ser_lbl.grid(column=0, row=2)

# Input box for number of serial numbers
num_ser_txt = Text(window, height=1, width=20)
num_ser_txt.grid(column=0, row=3)

# Enter button for the serial number
def generate():
    txt.delete('1.0', END)                              # Clear text box
    input_text = prod_code_txt.get("1.0", 'end-1c')          # 1 means line 1, 0 means character 0
    prod_code = input_text[0:2]                         # Read the first two characters to get prod code (string)
    starting_serial = input_text[2:].replace(" ", "")                   # Serial code is the remainder
    starting_serial = starting_serial.replace('\t', '')                       # Replace all tabs
    num_serials = int(num_ser_txt.get("1.0", 'end-1c'))      # Grab the number of serials

    # Convert serial number to integer
    starting_int = base36_to_int(starting_serial)

    for i in range(num_serials):
        ser_num = np.base_repr(starting_int + i, 36)
        str_ser_num = str(ser_num)
        appendstr = ''
        if len(str_ser_num) < len(starting_serial):
            appendnum = len(starting_serial) - len(str_ser_num)
            for j in range(appendnum):
                appendstr += '0'

        str_ser_num = appendstr + str_ser_num
        str_ser_num = prod_code + str_ser_num
        txt.insert(INSERT, str_ser_num + "\n")


gen_btn = Button(window, text='Generate', command=generate)
gen_btn.grid(column=0, row=4)

# Show list of serial numbers
txt = scrolledtext.ScrolledText(window, width=40,height=10)
txt.grid(column=0, row=6)

# Output button for create text file
def output_txt():
    window.withdraw()
    file_name = filedialog.asksaveasfilename(defaultextension=".txt")
    f = open(file_name, "w+")

    for line in txt.get('1.0', 'end-1c').splitlines():
        if line:
            f.write(line+'\n')

out_btn = Button(window, text='Output to Text', command=output_txt)
out_btn.grid(column=0, row=8)

window.geometry('350x400')
window.mainloop()