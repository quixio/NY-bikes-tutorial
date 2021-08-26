from quixstreaming import *

from datetime import datetime
import pandas as pd
import time
from datetime import timezone
from ny_bikes_API import get_agg_data

# Placeholder variables
certificatePath = {placeholder:broker.security.certificatepath}
username = {placeholder:broker.security.username}
password = {placeholder:broker.security.password}
broker = {placeholder:broker.broker}
topic_id = {placeholder:topic}

# Create a client factory. Factory helps you create StreamingClient (see below) a little bit easier
security = SecurityOptions(certificatePath, username, password)
client = StreamingClient(broker, security)

# Open output topic connection.
output_topic = client.open_output_topic(topic_id)

# CREATE A STREAM: collection of data that belong to a single session of a single source.
stream = output_topic.create_stream("NY-Real-Time-Bikes")
# Give the stream human readable name. This name will appear in data catalogue.
stream.properties.name = "New York Total Bikes Real Time"
# Save stream in specific folder in data catalogue to help organize your workspace.
stream.properties.location = "/NY_Real_Time"

while True:
    try:
        # Current timestamp
        current_time_i = datetime.now(timezone.utc)
        
        # ToL API Request
        df_i_agg = get_agg_data()
        total_bikes = df_i_agg.loc[0,'num_bikes_available']+df_i_agg.loc[0,'num_ebikes_available']                    

        # Write stream 
        stream.parameters.buffer.add_timestamp(current_time_i) \
            .add_value('total_num_bikes_available', total_bikes) \
            .add_value('num_docks_available', df_i_agg.loc[0,'num_docks_available']) \
            .write()

        # How long did the Request and transformation take
        current_time_j = datetime.now(timezone.utc)
        int_sec = int((current_time_j-current_time_i).seconds)
        print(current_time_i, current_time_j, int_sec, ' bikes: ', total_bikes)

    except Exception:
        print(traceback.format_exc())