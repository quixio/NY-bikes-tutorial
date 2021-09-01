from datetime import datetime
from quixstreaming import SecurityOptions, StreamingClient
from datetime import timezone
import traceback
from tfl_api import get_agg_bikepoint_data

"""
IMPORTANT
Open the tfl_api.py file and add your TFL API KEYS
"""

certificatePath = "{placeholder:broker.security.certificatepath}"
username = "{placeholder:broker.security.username}"
password = "{placeholder:broker.security.password}"
broker = "{placeholder:broker.address}"

# configure security objects
security = SecurityOptions(certificatePath, username, password)
client = StreamingClient(broker, security)

# Open output topic connection.
output_topic = client.open_output_topic('{placeholder:outputTopic}')

# CREATE A STREAM
# A stream is a collection of data that belong to a single session of a single source.
# Initiate streams
stream = output_topic.create_stream("Available-Bikes")

# Give the stream human readable name. This name will appear in data catalogue.
stream.properties.name = "Available Bikes Location"

# Save stream in specific folder in data catalogue to help organize your workspace.
stream.properties.location = "/Bikes"

stream.parameters.buffer.buffer_timeout = 1000
stream.parameters.buffer.time_span_in_milliseconds = 1000

while True:
    try:
        # Current timestamp
        current_time = datetime.now(timezone.utc)
        
        # ToL API Request
        df, df_agg = get_agg_bikepoint_data()
        
        # iterate over df rows (over bikepoints)
        for i, row in df.iterrows():
            stream.parameters.buffer.add_timestamp(current_time) \
                .add_tag('Id', row['id']) \
                .add_value('Name', row['Name']) \
                .add_value('Lat', row['lat']) \
                .add_value('Lon', row['lon']) \
                .add_value('NbBikes', row['NbBikes']) \
                .add_value('NbEmptyDocks', row['NbEmptyDocks']).write()

    except Exception:
        print(traceback.format_exc())
