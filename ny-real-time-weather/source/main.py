from datetime import datetime
import pandas as pd
import time
import os
from quixstreaming import *

from ny_weather_API import perform_API_request, get_current_weather, get_tomorrow_weather
from datetime import timezone

# Fill variables
certificatePath = "{placeholder:broker.security.certificatepath}"
username = "{placeholder:broker.security.username}"
password = "{placeholder:broker.security.password}"
broker = "{placeholder:broker.address}"
topic_id = "{placeholder:outputTopic}"

openweather_api_key = "{placeholder:openweatherkey}"

# Create a client factory. Factory helps you create StreamingClient (see below) a little bit easier
security = SecurityOptions(certificatePath, username, password)
client = StreamingClient(broker, security)

# Open output topic connection.
output_topic = client.open_output_topic(topic_id)

# CREATE A STREAM: A stream is a collection of data that belong to a single session of a single source.
stream = output_topic.create_stream("NY-Real-Time-Weather")
# Give the stream human readable name. This name will appear in data catalogue.
stream.properties.name = "New York Weather Real Time"
# Save stream in specific folder in data catalogue to help organize your workspace.
stream.properties.location = "/NY_Real_Time"

while True:
    try:
        # Current timestamp
        current_time = datetime.now(timezone.utc)

        # ToL API Request
        json_response = perform_API_request(openweather_api_key)
        df_now = get_current_weather(json_response)
        df_1d = get_tomorrow_weather(json_response)
        list_dfs = [df_now, df_1d]

        # Write stream
        for i, forecast_time in enumerate(['Current', 'NextDay']):
            stream.parameters.buffer.add_timestamp(current_time) \
                .add_tag('Forecast', forecast_time) \
                .add_value('feelslike_temp_c', list_dfs[i].loc[0, 'feelslike_temp_c']) \
                .add_value('wind_kph', list_dfs[i].loc[0, 'wind_mps'] * 3.6) \
                .add_value('condition', list_dfs[i].loc[0, 'condition']) \
                .write()

        # How long did the Request and transformation take
        current_time_j = datetime.now(timezone.utc)
        int_sec = int((current_time_j - current_time).seconds)
        print(current_time, current_time_j, int_sec)

        SLEEP_TIME = 1800  # Seconds to wait between API requests (30 mins)
        if int_sec < SLEEP_TIME:
            time.sleep(SLEEP_TIME - int_sec)

    except Exception:
        print(traceback.format_exc())