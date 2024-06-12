"""
Created 31/05/2024
@author: Jessica Murphy
"""

import argparse
# import numpy as np 
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import get_sun, EarthLocation, AltAz
# from astroplan import Observer
from datetime import datetime, timedelta, timezone
import subprocess

process = subprocess.Popen(['./sun_flare_prob'],stdout=subprocess.PIPE)
result  = process.communicate()
print(result)

# Function to round to the nearest 10 minutes
def minutes_rounded(dt):
    new_minute = (dt.minute // 10) * 10 # Calculate nearest lower multiple of 10
    if dt.minute % 10 >= 5: # Check if rounding up is needed
        new_minute += 10 
    return dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=new_minute) # Create rounded time

def day_rounded(dt):
    # Set to 1 minute past midnight UTC on date in question
    return dt.replace(hour=0,minute=0, second=0, microsecond=0) + timedelta(hours=0,minutes=1) 

def main (horizon, plot):
  # Set up Observer, Target, and observation time objects
  longitude = -7.9219 * u.deg
  latitude = 53.0950 * u.deg
  elevation = 72.0 * u.m
  location = EarthLocation.from_geodetic(longitude, latitude, elevation)
  
  # observer = Observer(name='I-LOFAR',
  #                    location=location,
  #                    description="LOFAR Station IE613")
  
  # Define the observation times, use only UTC
  start_time = day_rounded(datetime.now(timezone.utc))
  end_time = start_time + timedelta(days=2)
  delta_t = timedelta(minutes=10)  # time step
  times = [start_time + i * delta_t for i in range(int((end_time - start_time) / delta_t))]
  
  # Convert times to astropy Time objects
  astropy_times = Time(times)
  
  # Compute the sun's position in the sky
  altaz_frame = AltAz(obstime=astropy_times, location=location)
  sun_altaz = get_sun(astropy_times).transform_to(altaz_frame)
  
  # Extract the altitude
  sun_altitude = sun_altaz.alt
  
  # Initialise observation periods, stores the start & end times when sun is above horizon
  observation_periods = []
  start_observation = None
  
  # Find the periods when the sun's altitude is above the horizon
  for time, alt in zip(astropy_times, sun_altitude):
    if alt > horizon * u.deg: # check is altitude above horizon
      if start_observation is None: # check if new observation period is being started
        start_observation = time.datetime # set to current time since not in observation period
      end_observation = time.datetime # end at current time
    else: # check if below the horizon
      if start_observation is not None: # in observation period
        observation_periods.append((start_observation, end_observation))
        start_observation = None # observation period has ended
  
  # Add the last observation period if it ended with the sun above the horizon
  if start_observation is not None:
    observation_periods.append((start_observation, end_observation))
  
  # Print the observation periods
  if observation_periods:
    # Format the observation periods to exlude periods below horizon in a 24hr cycle
    periods_str = ' and '.join([f'{start.strftime("%Y-%m-%d %H:%M:%S")} to {end.strftime("%Y-%m-%d %H:%M:%S")}' for start, end in observation_periods])
    print(f'Observe during the following periods: {periods_str}')
  else:
    print('The sun does not rise above the specified horizon today.')
  
  # Plot the results - visualisation aid
  if(plot):
    import matplotlib.pyplot as plt
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

# Define function to parse command line arguments
def parse_arguments():
  parser = argparse.ArgumentParser(description='Plot sun elevation over time.') # create argument parser
  parser.add_argument('-horizon', type=float, default=30.0, help='Horizon angle (degrees) for filtering sun elevation') # add argument for horizon
  parser.add_argument('-plot', action='store_true',default=False, help='Plot solar elevation for next 24 hours')
  return parser.parse_args()

# Run script with specified horizon angle
if __name__ == '__main__':
  args = parse_arguments() # call function to parse command line arguments
  main(args.horizon, args.plot) # call main function


