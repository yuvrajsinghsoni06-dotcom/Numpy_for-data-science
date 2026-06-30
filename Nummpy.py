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

# score = np.array([91,100,55,73,83,64])

# score[score < 80] = 0
# print(score)


# """ broadcasting - It allows NumPy to perform operations on arrays with different shapes by virtually expanding dimensions so they match the dimensions of a larger array. For broadcasting to act on an array, they have the following descriptions:
# - Dimensions have the same size.
# - One dimension must be the same, or one of the dimensions must be one for both the array.
# That allows to perform element-wise operations like addition, subtraction, and element-wise multiplication on arrays of different sizes. It doesn't perform a dot product. Instead, it virtually stretches the smaller array to match the shape of the larger set, so the operation can be applied to the corresponding elements. 
# """

# arr1 =np.array([[1,2,3,4]])
# arr2 = np.array([[1],[2],[3],[4]])

# print(np.shape(arr1))
# print(np.shape(arr2))

# print(arr1 + arr2)


# array1 = np.array([[1,2,9,3,4,5,6,7,8]])
# array2 = np.array([[1],[2],[9],[3],[4],[5],[6],[7],[8]])

# print(np.shape(array1))
# print(np.shape(array2))

# print(array1 * array2)


# Aggregate function - Summarize data and typically returns are at a single value.  Basically utilizes certain built-in functions such as:
# - Sum of all element
# - mean
# - standard deviation
# - variance
# - min
# - max 
# include axis arg to specfy the method call when 0 will applied to column , when 1 applied to rows.


array = np.array([[1,2,3,4,5],
                  [6,7,8,9,10]])

# print(np.sum(array))
# print(np.mean(array))  # This is the mean of the array. 
# print(np.std(array))   # Standard deviation of array 
# print(np.var(array))  # Returns variants of an array. 
# print(np.max(array))   
# print(np.min(array))
# print(np.argmax(array))  # Returns the index position of the  max ele 
# print(np.argmin(array))  # Returns the index position of the  min ele



print(np.sum(array, axis =1))