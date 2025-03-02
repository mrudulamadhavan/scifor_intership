#Importing Libraries
import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split
from matplotlib import image

st.set_page_config(page_title="Bike Sharing Demand Predictor", page_icon="https://www.shutterstock.com/image-vector/bicycle-filled-outline-icons-vector-illustration-1772580485",
                   layout="centered")

#import model
st.title(":red[  Bike Sharing Demand Predictor  ]")

#resources path

FILE_DIR1 = os.path.dirname(os.path.abspath("miniproject//pages//Predictor.py"))
FILE_DIR = os.path.join(FILE_DIR1,os.pardir)
dir_of_interest = os.path.join(FILE_DIR, "resources")

IMAGE_PATH = os.path.join(dir_of_interest, "images", "predict.png")
img = image.imread(IMAGE_PATH)
st.image(img) 

DATA_PATH = os.path.join(dir_of_interest, "data")

#Load data
DATA_PATH1=os.path.join(DATA_PATH, "bike_demand_cleaned.csv")
df=pd.read_csv(DATA_PATH1,encoding='latin')
df1 = df.copy()

# ['Temperature(°C)', 'Humidity(%)', 'Wind speed (m/s)','Solar Radiation (MJ/m2)', 'Visibility (10m)', 'Month', 'Weekday','Hour', 'Holiday', 'Seasons', 'Rented Bike Count']

def prediction(season,month,weekday,hour,holiday,temperature,humidity,visibility,windspeed,solarrdn,rainfall):
    prediction = xgb.predict([[season,month,weekday,hour,holiday,temperature,humidity,visibility,windspeed,solarrdn]])
    print(prediction)
    return prediction

# ------------------------------------------------------------------------------------------------------------
st.subheader("Enter the location details :")

col1,col2,col3 = st.columns(3)
with col1:  
    season = st.selectbox("Season", df["Seasons"].unique())
with col2:  
    month = st.selectbox("Month", ['January', 'February', 'March', 'April', 'May','June', 'July', 'August', 'September', 'October', 'November','December'])
with col3:  
    weekday = st.selectbox("Weekday", ['Sunday', 'Monday', 'Tuesday', 'Wednesday','Thursday','Friday', 'Saturday'])

col4,col5 = st.columns(2)
with col4:  
    hour = st.selectbox("Time Shift", df["Hour"].unique())
with col5:  
  holiday = st.selectbox("Holiday", df["Holiday"].unique())

left_column, middle_column, right_column = st.columns(3)
with left_column:
    temperature = st.text_input("Temperature(°C)  ",value=0.0) 
with middle_column:
    humidity = st.text_input("Humidity(%) ",value=0)
with right_column:
    visibility = st.text_input("Visibility(10m)  ",value=0)

col1,col2 = st.columns(2)
with col1:  
    windspeed = st.number_input("Wind speed (m/s) ")
with col2:
    solarrdn = st.number_input("Solar Radiation (MJ/m2) ")

bike_count = 0

#---------------------------------------------------------------------------------------------------------------
#Create dataframe using all these values
sample=pd.DataFrame({"Seasons":[season],"Month":[month],"Weekday":[weekday],"Hour":[hour],"Holiday":["holiday"],
                    "Temperature(°C)":float(temperature),"Humidity(%)":float(humidity),"Visibility (10m)":float(visibility),
                    "Wind speed (m/s)":[windspeed],"Solar Radiation (MJ/m2)":[solarrdn]})

#Function to change season to number
def replace_season(season):    
    if season =='Summer':
        return 1.0
    elif season =='Winter':
        return 2.0
    elif season =='Spring':
        return 3.0
    else:
        return 4.0
df['Seasons'] = df['Seasons'].apply(replace_season)
sample['Seasons'] = sample['Seasons'].apply(replace_season)

def month_name(month):
    if month == 'January':
        return 1.0
    elif month ==  'February':
        return 2.0
    elif month == 'March':
        return 3.0
    elif month == 'April':
        return 4.0
    elif month == 'May':
        return 5.0
    elif month == 'June':
        return 6.0
    elif month == 'July':
        return 7.0
    elif month == 'August':
        return 8.0
    elif month == 'September':
        return 9.0
    elif month == 'October':
        return 10.0
    elif month == 'November':
        return 11.0
    else:
        return 12.0

df['Month'] = df['Month'].apply(month_name).astype('float64')
sample['Month'] = sample['Month'].apply(month_name).astype('float64')


def replace_weekday(weekday):
    if weekday =='Sunday':
        return 1.0
    elif weekday=='Monday':
        return 2.0
    elif weekday=='Tuesday':
        return 3.0
    elif weekday=='Wednesday':
        return 4.0
    elif weekday=='Thursday':
        return 5.0
    elif weekday =='Friday':
        return 6.0
    else:
        return 7.0
df['Weekday'] = df['Weekday'].apply(replace_weekday).astype('float64')
sample['Weekday'] = sample['Weekday'].apply(replace_weekday).astype('float64')

# Function to distribute hour
def distribute_hour(hour):
    if hour == '12 AM - 4 AM':
        return 0.0  # 
    elif hour == '4 AM - 8 AM':
        return 1.0 # 
    elif hour == '8 AM - 12 PM':
        return 2.0 #
    elif hour == '12 PM - 4 PM':
        return 3.0
    elif hour == '4 PM - 8 PM':
        return 4.0
    elif hour == '8 PM - 12 AM':
        return 5.0
    else:
        pass


df['Hour'] = df['Hour'].apply(distribute_hour).astype('float64')
sample['Hour'] = sample['Hour'].apply(distribute_hour).astype('float64')

def replace_holiday(holiday):
    if holiday =='No':
        return 0.0
    else:
        return 1.0
df['Holiday'] = df['Holiday'].apply(replace_holiday)
sample['Holiday'] = sample['Holiday'].apply(replace_holiday)

df['Wind speed (m/s)'] = np.sqrt(df['Wind speed (m/s)'])
sample['Wind speed (m/s)'] = np.sqrt(sample['Wind speed (m/s)'])

#Split data into X and y
X=df.drop('Rented Bike Count', axis=1).values
y=df['Rented Bike Count'].values

#Standarizing the features
std=StandardScaler()
std_fit=std.fit(X)
X=std_fit.transform(X)

# Splitting data into 75:25 ratio
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

#Train the model
xgb=XGBRegressor(learning_rate=0.15, n_estimators=50, max_leaves=0, random_state=42)
xgb.fit(X,y)

#Standardize the features
sample=sample.values
sample=std_fit.transform(sample)
st.write("")
#Prediction
if st.button('Predict Demand',key = "<uniquevalueofsomesort>"):
    bike_count=xgb.predict(sample)
    bike_count=bike_count[0] 
    st.subheader(":blue[Mean Count of Bike Rentals :] :green[{}]".format(str(round(abs(bike_count)))))
else:
    pass
    
