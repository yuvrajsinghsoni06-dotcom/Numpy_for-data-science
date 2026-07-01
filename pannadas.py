import pandas as pd


# series - A one-dimensional labeled array. Think of it as the column in a spreadsheet which contains a same type of data in them. Series is a contructor not a function


data = [1,2,3,4,5]
series = pd.Series(data, index = ["a","b","c","d","e"])
# print(series)

# loc = property which allows to accces the elements of a series by its lable(index) 
# series.loc["a"] = 1000

# print(series)

# iloc = property which allows to access the ele of a series by its int position

# print(series.iloc[0])

# print(series[series > 2.5])  # i can apply filter in a series of data

calories = {"day1": 2230, "day2": 2500, "day3" : 2000}
series = pd.Series(calories)

series.loc["day1"] = 2800
# print(series)

print(series[series <= 2500])