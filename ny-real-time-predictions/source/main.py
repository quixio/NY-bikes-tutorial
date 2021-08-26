import pandas as pd

from quixstreaming import *
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
import signal
import threading

from model_functions import get_saved_models, predict_bikes_availability_and_write_into_streams

# Fill variables
certificatePath = {placeholder:broker.security.certificatepath}
username = {placeholder:broker.security.username}
password = {placeholder:broker.security.password}
broker = {placeholder:broker.broker}
input_bikes_topic_id = {placeholder:topic_input_bikes}
input_weather_topic_id = {placeholder:topic_input_weather}
output_prediction_topic_id = {placeholder:topic_output_prediction}

# Create a client factory. Factory helps you create StreamingClient (see below) a little bit easier
security = SecurityOptions(certificatePath, username, password)
client = StreamingClient(broker, security)

# Open input and output topic connections.
input_topic_bikes = client.open_input_topic(input_bikes_topic_id)
input_topic_weather = client.open_input_topic(input_weather_topic_id)
output_topic = client.open_output_topic(output_prediction_topic_id)

# CREATE A STREAM: collection of data that belong to a single session of a single source.
stream_0 = output_topic.create_stream("NY-Real-Time-Bikes-NY-Timestamp")
stream_0.properties.name = "Number of available bikes in NY with local NY timestamp"
stream_0.properties.location = "/ML_Predictions"
stream_1 = output_topic.create_stream("PRED_ML_1h")
stream_1.properties.name = "Prediction ML Model 1-hour ahead forecast"
stream_1.properties.location = "/ML_Predictions"
stream_2 = output_topic.create_stream("PRED_ML_1d")
stream_2.properties.name = "Prediction ML Model 1-day ahead forecast"
stream_2.properties.location = "/ML_Predictions"

# Get saved models
ml_model_1h, ml_model_1day = get_saved_models()

# Initiate empty dataframes for bikes and weather data
df_bikes = pd.DataFrame()
df_weather = pd.DataFrame()

# define callback for bike streams
def read_bike_stream(new_stream: StreamReader):
    print("New bike stream read:" + new_stream.stream_id)

    def on_parameter_data_handler(df: pd.DataFrame):        
        global df_bikes
        df_bikes = df.copy(deep=True)        
        predict_bikes_availability_and_write_into_streams(df_bikes, df_weather, ml_model_1h, ml_model_1day, stream_0, stream_1, stream_2)

    new_stream.parameters.on_read_pandas += on_parameter_data_handler

# define callback for weather streams
def read_weather_stream(new_stream: StreamReader):
    
    buffer_options = ParametersBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100
    buffer_options.buffer_timeout = 100
    buffer = new_stream.parameters.create_buffer(buffer_options)

    print("New weather stream read:" + new_stream.stream_id)

    def on_parameter_data_handler(df: pd.DataFrame):        
        global df_weather
        df_weather = df.copy(deep=True)        
        predict_bikes_availability_and_write_into_streams(df_bikes, df_weather, ml_model_1h, ml_model_1day, stream_0, stream_1, stream_2)

    buffer.on_read_pandas += on_parameter_data_handler    


# Hook up events before initiating read to avoid losing out on any data
input_topic_bikes.on_stream_received += read_bike_stream
input_topic_weather.on_stream_received += read_weather_stream
input_topic_weather.start_reading()  # initiate read for weather data
input_topic_bikes.start_reading()  # initiate read for bike data

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")


event = threading.Event() 
def signal_handler(sig, frame):
    print('Exiting...')
    event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
event.wait()