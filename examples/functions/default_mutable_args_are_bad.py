"""
Do not use mutable values as default in function parameters.

It has side-effect that you most probably do not need.
"""


def append(value, collection=[]):
    collection.append(value)
    return collection


print("Calling append first time.")
result_1 = append(1)
print("Result of first call:", result_1)  # [ 1 ]

print()
print("Calling append second time.")
result_2 = append(2)
print("Result of second call:", result_2)  # [ 1, 2 ]
print("Result of first call after second call:", result_1)  # [ 1, 2 ]
print("Are results the same object:", result_1 is result_2)
