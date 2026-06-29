import numpy as np



# print(np.__version__)

# my_list = [1,2,3,4]
# my_list = my_list * 2

# print(my_list)
# arr = np.array([1,2,3,4,5])
# arr = arr * 2
# print(arr)

# print(type(arr))


# array = np.array([[["A","b","c"], ["d","e","f"], ["i","j","k"]],
#                   [["k","l","m"], ["n","o","p"], ["q","r","s"]],
#                   [["t","u","v"], ["w","x","y"], ["z","o","g"]]])
# # print(array.ndim)  # ndim - attribute calcluates no of dimension of arr
# # print(array.shape) # shape - attribute It calculates the number of rows, columns, and number of layers in an array. 


# # chain indexing - A multi-dimensional indexing (arr[layer_no,row_no,column_no])
# print(array[1,1,0])

# master =array[2,1,2] +  array[2,0,1] + array[2,0,2] + array[1,2,1] + array[0,0,0] + array[0,2,1]
# print(master)

# slicing - arr[start:end:steps]

# uv =np.array([[1,2,3],
#               [1,1,2],
#               [4,5,6],
#               [7,8,9]])

# print(uv[2:,1:])  # for column like indexing we arr[:, indexing]


#scalar arthimthics -- 


# arr = np.array([1,2,3])

# # print(arr  + 2)
# # print(arr - 2)
# # print(arr  * 2)
# # print(arr   /  2)
# # print(arr   //  2)
# # print(arr   **  2)

# # vectororization math func-- applies a function to a array without writing the loop

# # print(np.sqrt(arr))
# # print(np.round(arr))
# # print(np.floor(arr))  # floor - for rounding down of ele
# # print(np.ceil(arr))  # ceil - for round up of ele

# area = np.pi * (arr ** 2)
# print(area)

# element wise arthimathic

# arr1 = np.array([1,2,3])
# arr2 = np.array([4,5,6])

# print(arr1 + arr2)
# print(arr1 - arr2)
# print(arr1 * arr2)
# print(arr1 / arr2)
# print(arr1 ** arr2)

# Comparison Operators -  returns a boolen outputs

score = np.array([91,100,55,73,83,64])

score[score < 80] = 0
print(score)
