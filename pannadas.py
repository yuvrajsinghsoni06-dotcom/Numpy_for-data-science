import pandas as pd


# series - A one-dimensional labeled array. Think of it as the column in a spreadsheet which contains a same type of data in them. Series is a contructor not a function


data = [1,2,3,4,5]
series = pd.Series(data, index = ["a","b","c","d","e"])
# print(series)

# loc = property which allows to accces the elements of a series by its lable(index) (location by label) ccan also be used in dataframe
# series.loc["a"] = 1000

# print(series)

# iloc = property which allows to access the ele of a series by its int position

# print(series.iloc[0])

# print(series[series > 2.5])  # i can apply filter in a series of data

# calories = {"day1": 2230, "day2": 2500, "day3" : 2000}
# series = pd.Series(calories)

# series.loc["day1"] = 2800
# # print(series)

# print(series[series <= 2500])



# dataframe - It's a two-dimensional label data structure with columns and rows, similar to a spreadsheet or a SQL table. 

# data = {"Name": ["morphes", "john smith", "neo", "trinity"],
#         "Id" : [1,2,3,4] ,
#         "Salary" : [10000,20000,30000,10000]}

# dataframe = pd.DataFrame(data, index = ["employee1", "employee2","employee3","employee4"])
# # print(dataframe.loc["employee3"])


# print(dataframe.iloc[3])

# dataframe["Role"] = ["Cammander", "Agent" , "the Chosen One", "the baddie"]   #  Addition of new column in df

# # addition of new row in df - so we forst create a seperate dataframe and then concat it into exixting dataframe
# df_row = pd.DataFrame({"Name": "matrix", "Id" : 5, "Salary" : 50000,
#                        "Role" : "the world of illusion"}, index = ["employee5"])
# df_row1 = pd.DataFrame({"Name": "sexy red dress women", "Id" : 6, "Salary" : 50000,
#                        "Role" : "the hot latina"}, index = ["employee6"])
# df_row2 = pd.DataFrame({"Name": "rick", "Id" : 5, "Salary" : 50000,
#                        "Role" : "the crazy piece of shit"}, index = ["employee7"])
# dataframe = pd.concat([dataframe, df_row, df_row1, df_row2])
# print(dataframe)

# df = pd.read_csv("pokemon.csv")  # to read a csv file using pandas
# print(df.to_string())

# df = pd.read_json("pokemon.json")  # to read a json file using pandas
# print(df)

# df = pd.read_csv("pokemon.csv" , index_col = "Name")


# selection of column using column name

# print(df["Name"].to_string())
# print(df["Height"].to_string())
# print(df["Weight"].to_string())

# selection of multiple coljumn -
# print(df[["Name", "Height", "Weight"]].to_string())


# selction by Rows -
# print(df.loc["Mewtwo"])

# Notice the capital 'T', the space, and the capital 'H'
# print(df.loc["Gastly":"Mewtwo", ["Weight", "Height"]])


# print(df.iloc[0:11, 0:5])


# pokemon = input(f"Enter Pokemon Name: ")

# try:
#     print(df.loc[pokemon])
# except KeyError:
#     print(f"{pokemon} not found")


# filtering

# print(df[df["Height"] > 2.0])

# legendery_pokemon = df[df["Legendary"] == True]
# print(legendery_pokemon)

# water_pok = df[(df["Type1"] == "Water") & (df["Type2"] != "Water")]
# print(water_pok)


# Aggerate function - reduces the set of values into single summary value used to anlayse data
  

  # applies to whole data frame
# df = pd.read_csv("pokemon.csv")
# print(df.mean(numeric_only= True))
# print(df.sum(numeric_only= True))
# print(df.min(numeric_only= True))
# print(df.max(numeric_only= True))
# print(df.count())


# applies to a single column

# print(df["Height"].mean())
# print(df["Height"].sum())
# print(df["Height"].min())
# print(df["Height"].max())
# print(df["Height"].count())

# groupby() - used to group data based on a column and then apply aggerate function on it

# group = df.groupby("Type1")
# print(group["Weight"].count())



# data cleaning - process of removing or fixing incorrect, corrupted, incorrectly formatted, duplicate, or incomplete data within a dataset

df = pd.read_csv("pokemon.csv")

# drop a column - removal of column 

# df = df.drop(columns = ["Legendary", "Type2"])
# print(df.to_string())


# handle of missing data - missing data can be handled by either removing the rows or columns with missing data or by filling the missing data with a specific value

# df = df.dropna(subset = ["Type2"])

# df = df.fillna({"Type2": "None"})
# print(df.to_string())



# fix inconsistent values - inconsistent values can be fixed by replacing the incorrect values with the correct values

# df["Type1"] = df["Type1"].replace({"Fire": "Flame",
#                                     "Water": "Aqua",
#                                     "Grass": "Leaf"})
# print(df.to_string())


# df["Name"] = df["Name"].str.upper()
# print(df[df["Legendary"] == True].to_string())



# fix data types - data types can be fixed by converting the data types of the columns to the correct data types

df["Legendary"] = df["Legendary"].astype(bool)
print(df.to_string())

