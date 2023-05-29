import os
import templates

main_cc = templates.main
main_functions_h = templates.main_functions
output_handler_cc = templates.output_handler_cc
output_handler_h = templates.output_handler_h
constants_h = templates.constants_h
constants_cc = templates.constants_cc

result_a = main_cc.substitute()
result_b = main_functions_h.substitute()
result_c = output_handler_cc.substitute()
result_d = output_handler_h.substitute()
result_e = constants_h.substitute()
result_f = constants_cc.substitute()

file_path_a = os.path.join("main", "main.cc")
with open(file_path_a, "w") as file_a:
    file_a.write(result_a)

file_path_b = os.path.join("main", "main_functions.h")
with open(file_path_b, "w") as file_b:
    file_b.write(result_b)

file_path_c = os.path.join("main", "output_handler.cc")
with open(file_path_c, "w") as file_c:
    file_c.write(result_c)

file_path_d = os.path.join("main", "output_handler.h")
with open(file_path_d, "w") as file_d:
    file_d.write(result_d)

file_path_e = os.path.join("main", "constants.h")
with open(file_path_e, "w") as file_e:
    file_e.write(result_e)

file_path_f = os.path.join("main", "constants.cc")
with open(file_path_f, "w") as file_f:
    file_f.write(result_f)
