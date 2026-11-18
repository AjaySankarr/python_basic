# file = open('./info.txt','r')
# print("file",file)

# # Read:
# with open("./info.txt",'r') as file:
#     data = file.readlines()

#     print("data", data)

# with open("./info.txt", "w") as file:

#     file.write("Raj\n")
#     file.write("Ajay\n")
#     file.write("Vijay\n")

# Now you want to add Vijay without deleting the existing data.

# with open("students.txt", "a") as file:

#     file.write("Sankar\n")

# Why do we use with open()
# file = open("students.txt", "r")

# data = file.read()

# file.close()

# We manually close the file using close().

# What happens if an exception occurs before file.close()?

# The file might remain open longer than expected.

# Instead, Python provides a context manager using with.

# with open("students.txt", "r") as file:

#     data = file.read()

#     print(data)

# tell() returns the current position of the file pointer.
# with open("students.txt", "r") as file:

#     print(file.tell())

#     data = file.read(3)

#     print(data)

#     print(file.tell())

# seek() moves the file pointer to a particular position.
# with open("students.txt", "r") as file:

#     print(file.read(3))

#     file.seek(0)

#     print(file.read(3))



