"""

SPDX-FileCopyrightText: 2023 Espressif Systems (Shanghai) CO LTD

SPDX-License-Identifier: Apache-2.0

"""

# import necessary modules
import subprocess
import os
import re
import argparse
import templates

# subprocess to run generate_cc_array.py
"""
RUN from tools
> python generate_cc_arrays.py main hello_world.tflite 
"""

parser = argparse.ArgumentParser(
    description="Description: Accept .tflite or .bmp file as input from the user"
)
parser.add_argument("input_file", help=".tflite or .bmp format")
args = parser.parse_args()
tflite_file = args.input_file

# extract model name from .tflite file
x = tflite_file.split(".")[0]

generate_cc_array = [
    "python",
    "generate_cc_arrays.py",
    f"{x}/main",
    tflite_file,
]
subprocess.run(generate_cc_array, check=True)

# subprocess to run generate_micromutable_op_resolver.py
"""
RUN from tools
> python gen_micro_mutable_op_resolver/generate_micro_mutable_op_resolver_from_model.py --common_tflite_path=. --input_tflite_files=hello_world.tflite --output_dir=main
"""
generate_micromutable_op_resolver = [
    "python",
    "gen_micro_mutable_op_resolver/generate_micro_mutable_op_resolver_from_model.py",
    "--common_tflite_path=.",
    f"--input_tflite_files={tflite_file}",
    f"--output_dir={x}/main",
]
subprocess.run(generate_micromutable_op_resolver, check=True)

# subprocess to generate .cc and .h templates
# generate_main_templates = ["python", "generate_main_templates.py"]
# subprocess.run(generate_main_templates, check=True)

# extract operations from gen_micro_mutable_op_resolver.h
with open(f"{x}/main/{x}_gen_micro_mutable_op_resolver.h") as cppfile:
    operations = []
    for line in cppfile:
        if "micro_op_resolver." in line:
            # print(line)
            line = "".join(line.split())
            operations.append(line)
# print(operations)

# extract the name of the unsigned integer array
with open(f"{x}/main/{x}_model_data.cc", "r") as file:
    cpp_content = file.read()

pattern = r"const\s+unsigned\s+char\s+(\w+)\[\]"
match = re.search(pattern, cpp_content)

if match:
    array_name = match.group(1)
    print("/*")
    print("Array name:", array_name)
else:
    print("Array name not found.")


"""
Format the unsigned int array from model_data.cc file
"""
with open(f"{x}/main/{x}_model_data.cc", "r+") as file:
    cpp_code = file.read()

    start_index = cpp_code.find("alignas(16) const unsigned char")
    end_index = cpp_code.find("};", start_index)

    array_string = cpp_code[start_index:end_index]

    elements = [element.strip() for element in array_string.split(",")]

    formatted_elements = []
    for i, element in enumerate(elements):
        if len(element) == 3:
            if element == "0x0":
                element = "0x00"
            else:
                element = element[:2] + "0" + element[2:]
        formatted_elements.append(element)

    formatted_array_lines = []
    for i in range(0, len(formatted_elements), 12):
        line_elements = formatted_elements[i : i + 12]
        line = ", ".join(line_elements)
        formatted_array_lines.append(line)

    formatted_array_string = ",\n".join(formatted_array_lines)

    formatted_cpp_code = (
        cpp_code[:start_index] + formatted_array_string + cpp_code[end_index:]
    )

    file.seek(0)
    file.truncate()
    file.write(formatted_cpp_code)

# VARIABLES
model_name = array_name
num_of_operations = len(operations)
resolver = "micro_op_resolver"
model_name_header = x
print("Name of the Model:", model_name)
print("Number of Operations:", num_of_operations)
print("Model Name Header:", model_name_header)
print("Description of Operations: ")
for i in operations:
    print(i)
print("*/")

results = templates.cppTemplate.safe_substitute(
    model_name=array_name,
    num_of_operations=num_of_operations,
    resolver=resolver,
    model_name_header=x,
)
cmake_template = templates.CMakeLists_txt.safe_substitute(model_name_header=x)

# store the results in main_functions.cc inside main folder
folder_path = f"{x}/main"
file_path = os.path.join(folder_path, "main_functions.cc")

with open(file_path, "w") as file:
    file.write(results)

# x is passed to ${model_header_name} and written inside CMakeLists.txt
file_path_cmake = os.path.join(folder_path, "CMakeLists.txt")
with open(file_path_cmake, "w") as file:
    file.write(cmake_template)

"""
The following code generates:
- main.cc
- main_functions.h
- output_handler.cc
- output_handler.h
- constants.h
- constants.cc
- Top Level: CMakeLists.txt
"""

main_cc = templates.main_cc
main_functions_h = templates.main_functions
output_handler_cc = templates.output_handler_cc
output_handler_h = templates.output_handler_h
constants_h = templates.constants_h
constants_cc = templates.constants_cc
CMakeLists_txt = templates.CMakeLists_txt
topLevelCMakeList = templates.topLevelCMake

result_a = main_cc.substitute()
result_b = main_functions_h.substitute()
result_c = output_handler_cc.substitute()
result_d = output_handler_h.substitute()
result_e = constants_h.substitute()
result_f = constants_cc.substitute()
result_g = topLevelCMakeList.safe_substitute()

files = {
    "main.cc": result_a,
    "main_functions.h": result_b,
    "output_handler.cc": result_c,
    "output_handler.h": result_d,
    "constants.h": result_e,
    "constants.cc": result_f,
}

# top level CMakeLists.txt
directory = f"{x}/main"
for filename, result in files.items():
    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        print(filename)
        file.write(result)

file_path_topCMake = os.path.join(f"{x}", "CMakeLists.txt")
with open(file_path_topCMake, "w") as file_g:
    file_g.write(result_g)
