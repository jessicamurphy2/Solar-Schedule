import numpy as np 
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astroplan import Observer
from datetime import datetime, timedelta

# Set up Observer, Target, and observation time objects
longitude = 7.9219 * u.deg
latitude = 53.0950 * u.deg
elevation = 72.0 * u.m
location = EarthLocation.from_geodetic(longitude, latitude, elevation)

observer = Observer(name='I-LOFAR',
                    location=location,
                    description="LOFAR Station IE613")

# Define the observation times
start_time = datetime.now()
end_time = start_time + timedelta(days=1)
delta_t = timedelta(minutes=10)  # time step
times = np.arange(start_time, end_time, delta_t).astype(datetime)

# Convert times to astropy Time objects
astropy_times = Time(times)

# Compute the sun's position in the sky
altaz_frame = AltAz(obstime=astropy_times, location=location)
sun_altaz = get_sun(astropy_times).transform_to(altaz_frame)

# Extract the altitude
sun_altitude = sun_altaz.alt

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(astropy_times.datetime, sun_altitude, label='Sun Elevation')
plt.xlabel('Time')
plt.ylabel('Sun Elevation (degrees)')
plt.title('Sun Elevation Over Time')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()