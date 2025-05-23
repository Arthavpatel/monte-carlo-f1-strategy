import fastf1 as f1
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
# ----------------- SETUP: Data Extraction -------------------
simulations = 10000
grand_prix = "Spanish Grand Prix"
race_length = 66


cache = '/Users/arthavpatel/Desktop/project/f1_cache'
f1.Cache.enable_cache(cache)
session = f1.get_session(2024, grand_prix, 'R')
session.load()


laps = session.laps
clean_laps = laps[
   (laps['Driver'] == 'VER') &
   (laps['IsAccurate'] == True) &
   (laps['PitInTime'].isna()) &
   (laps['PitOutTime'].isna()) &
   (laps['Deleted'] == False)
].copy()




clean_laps['LapTimeSeconds'] = clean_laps['LapTime'].dt.total_seconds()
avg_time_seconds = clean_laps['LapTimeSeconds'].mean()


# Avg Pit Stop Time
ver_laps = laps[laps['Driver'] == 'VER'].copy()
ver_laps = ver_laps[['LapNumber', 'PitInTime', 'PitOutTime']].reset_index(drop=True)
pit_stops = []
for i in range(len(ver_laps) - 1):
   in_time = ver_laps.loc[i, 'PitInTime']
   out_time = ver_laps.loc[i + 1, 'PitOutTime']


   if pd.notna(in_time) and pd.notna(out_time):
       duration = (out_time - in_time).total_seconds()
       lap = ver_laps.loc[i, 'LapNumber']
       pit_stops.append({
           'Lap': lap,
           'PitInTime': in_time,
           'PitOutTime': out_time,
           'PitDuration': duration
       })
pit_df = pd.DataFrame(pit_stops)
avg_pit_time = pit_df['PitDuration'].mean()
plt.figure(figsize=(8, 4))
plt.bar(pit_df['Lap'], pit_df['PitDuration'], color='orange')
plt.title("Max Verstappen Pit Stop Durations - Spanish GP 2024")
plt.xlabel("Lap")
plt.ylabel("Pit Duration (s)")
plt.grid(True)
plt.show()




# Degradations
def calculate_degradation(compound, compound_name, fallback):
   degradations = []
  
   if compound.empty:
       print(f"No {compound_name} Tyres were used in this GRAND PRIX")
       return fallback


   compound_stints = compound.groupby('Stint')
   for stint_num, stint in compound_stints:
       stint = stint.sort_values('LapNumber')
       if len(stint) < 3:
           continue
       first = stint['LapTimeSeconds'].iloc[0]
       last = stint['LapTimeSeconds'].iloc[-1]
       degradation = (last - first) / (len(stint) - 1)
       degradations.append(degradation)


   return np.mean(degradations) if degradations else None


default_soft_deg = 0.10
default_medium_deg = 0.05
default_hard_deg = 0.02


soft_stint = clean_laps[clean_laps['Compound'] == 'SOFT']
medium_stint = clean_laps[clean_laps['Compound'] == 'MEDIUM']
hard_stint = clean_laps[clean_laps['Compound'] == 'HARD']


avg_soft_degradation = calculate_degradation(soft_stint, "Soft", default_soft_deg)
avg_medium_degradation = calculate_degradation(medium_stint, "Medium", default_medium_deg)
avg_hard_degradation = calculate_degradation(hard_stint, "Hard", default_hard_deg)


def plot_all_degradation():
   plt.figure(figsize = (10,6))
   for compound_df, compound_name, color in [
       (soft_stint, "Soft", 'red'),
       (medium_stint, "Medium", 'g'),
       (hard_stint, "Hard", 'b')
   ]:
       if compound_df.empty:
           print(f"No {compound_name} Tyres were used in {grand_prix}")
           continue
      
       compound_stint = compound_df.groupby('Stint')
       for stint_num, stint in compound_stint:
           stint = stint.sort_values('LapNumber')
           if len(stint) < 3:
               continue
           plt.plot(
               stint['LapNumber'],
               stint['LapTimeSeconds'],
               label = f'{compound_name} - Stint {stint_num}'
           )
   plt.title(f"Tyre Degradation of {grand_prix}")
   plt.xlabel('Lap Number')
   plt.ylabel('Lap Time (s)')
   plt.legend()
   plt.grid(True)
   plt.show()
plot_all_degradation()
# Safety Car Deployment
years = range(2017, 2024)
total_safety_cars = 0
total_virtual_safety_car = 0
total_red_flags = 0
total_races = len(years)
for i in years:
   try:
       session = f1.get_session(i, grand_prix, 'R')
       session.load()
       track_status = session.track_status
       track_status['Status'] = track_status['Status'].astype(str)


       unique_flags = track_status['Status'].unique()
       is_red_flag = '6' in unique_flags
       is_sc = '4' in unique_flags
       is_vsc = '5' in unique_flags




       if is_sc and not is_red_flag:
           total_safety_cars += 1 
       if is_sc and is_red_flag:
           total_red_flags += 1        
       if is_vsc:
           total_virtual_safety_car += 1
   except:
       print(f"Failed to load {i}")


total_prob_SC = total_safety_cars / total_races
total_prob_VSC = total_virtual_safety_car / total_races
total_prob_red_flag = total_red_flags / total_races


# Total Variables
print("--------------------------------------------------------------------")
print(f"Total Simulations: {simulations}")
print(f"Total laps in {grand_prix}: {race_length}")
print(f"Average lap time of Max Verstappen: {avg_time_seconds:.3f} sec")
print(f"Average pit time: {avg_pit_time:.1f} sec")
print("--------------------------------------------------------------------")
print("Average degradations of compounds")
print(f"Soft Tyres: {avg_soft_degradation:.3f} sec/lap")
print(f"Medium Tyres: {avg_medium_degradation:.3f} sec/lap")
print(f"Hard Tyres: {avg_hard_degradation:.3f} sec/lap")
print("--------------------------------------------------------------------")
print(f"Total Safety Car Probability: {total_prob_SC:.1%}")
print(f"Total Virtual Safety Car Probability: {total_prob_VSC:.1%}")
print(f"Total Red Flag Probability: {total_prob_red_flag:.1%}")


# ----------------- DRIVER PROFILE -------------------
class CarDriverProfile:
   def __init__(self, name, base_lap_time, avg_pit_time, soft_deg,
                medium_deg, hard_deg, variability_range,
                safety_car_chance, virtual_safety_car_chance,
                race_length,
                safety_car_laps=(2, 5), sc_speed_factor=0.75,
                virtual_safety_car_laps=(1, 3), vsc_speed_factor=0.75,
                fuel_burn_rate=1.7, fuel_penalty_per_kg=0.035,
                red_flag_chance=total_prob_red_flag, red_flag_time_saving=20):
      
       self.name = name
       self.base_lap_time = base_lap_time
       self.avg_pit_time = avg_pit_time
       self.soft_deg = soft_deg
       self.medium_deg = medium_deg
       self.hard_deg = hard_deg
       self.variability_range = variability_range


       self.safety_car_chance = safety_car_chance
       self.safety_car_laps = safety_car_laps
       self.sc_speed_factor = sc_speed_factor


       self.virtual_safety_car_chance = virtual_safety_car_chance
       self.virtual_safety_car_laps = virtual_safety_car_laps
       self.vsc_speed_factor = vsc_speed_factor


       self.race_length = race_length


       self.fuel_burn_rate = fuel_burn_rate
       self.fuel_penalty_per_kg = fuel_penalty_per_kg


       self.red_flag_chance = red_flag_chance
       self.red_flag_time_saving = red_flag_time_saving


verstappen = CarDriverProfile(
   name="Max Verstappen",
   base_lap_time=avg_time_seconds,
   avg_pit_time=avg_pit_time,
   soft_deg=avg_soft_degradation,
   medium_deg=avg_medium_degradation,
   hard_deg=avg_hard_degradation,
   variability_range=(-0.1, 0.1),
   safety_car_chance=total_prob_SC,
   virtual_safety_car_chance=total_prob_VSC,
   race_length=race_length,
   vsc_speed_factor=(0.65, 0.75) ,
   fuel_burn_rate=1.7,
   fuel_penalty_per_kg=0.035,
   red_flag_chance=total_prob_red_flag,       
   red_flag_time_saving=15    
)




# ----------------- SIMULATION FUNCTIONS -------------------


def simulate_race(driver_profile, tire_stints):
   total_time = 0
   laps = 0


   degradation = {
       "Soft": driver_profile.soft_deg,
       "Medium": driver_profile.medium_deg,
       "Hard": driver_profile.hard_deg
   }


   fuel_left = driver_profile.fuel_burn_rate * driver_profile.race_length


   sc_deployed = random.random() < driver_profile.safety_car_chance
   sc_laps = random.randint(*driver_profile.safety_car_laps) if sc_deployed else 0
   sc_start = random.randint(10, driver_profile.race_length - sc_laps - 5) if sc_deployed else -1


   vsc_deployed = random.random() < driver_profile.virtual_safety_car_chance
   vsc_laps = random.randint(*driver_profile.virtual_safety_car_laps) if vsc_deployed else 0
   vsc_start = random.randint(10, driver_profile.race_length - vsc_laps - 3) if vsc_deployed else -1


   red_flag_deployed = random.random() < driver_profile.red_flag_chance
   red_flag_lap = random.randint(10, driver_profile.race_length - 10) if red_flag_deployed else -1
   red_flag_applied = False 


   for i, (compound, stint_length) in enumerate(tire_stints):
       for stint_lap in range(stint_length):
           laps += 1
           if laps > driver_profile.race_length:
               break


           deg_penalty = degradation[compound] * stint_lap
           random_variation = random.uniform(*driver_profile.variability_range)
           fuel_left -= driver_profile.fuel_burn_rate
           fuel_effect_per_lap = 0.04
           lap_time = (
               driver_profile.base_lap_time
               + deg_penalty
               + random_variation
               - (laps * fuel_effect_per_lap)
           )


           if sc_deployed and sc_start <= laps <= sc_start + sc_laps:
               lap_time /= driver_profile.sc_speed_factor


           elif vsc_deployed and vsc_start <= laps <= vsc_start + vsc_laps:
               lap_time /= random.uniform(*driver_profile.vsc_speed_factor)


           if red_flag_deployed and not red_flag_applied and laps == red_flag_lap:
               lap_time -= driver_profile.red_flag_time_saving
               red_flag_applied = True


           total_time += lap_time


       if i < len(tire_stints) - 1:
           pit_time = driver_profile.avg_pit_time
           if compound.upper() == "SOFT":
               pit_window = (15, 25)
           elif compound.upper() == "MEDIUM":
               pit_window = (25, 40)
           else:
               pit_window = (0, 0)


           if sc_deployed and pit_window[0] <= sc_start <= pit_window[1]:
               pit_time -= 8 


           total_time += pit_time
   return total_time






def monte_carlo_simulation(driver_profile, tire_stint, simulation=simulations):
   return [simulate_race(driver_profile, tire_stint) for _ in range(simulation)]


# ----------------- STRATEGY COMPARISON -------------------
strategy_pool = [
   [("Soft", 20), ("Medium", 25), ("Soft", 21)],
   [("Medium", 22), ("Soft", 22), ("Medium", 22)],
   [("Medium", 20), ("Medium", 23), ("Soft", 23)],
   [("Hard", 20), ("Medium", 28), ("Soft", 18)],
   [("Soft", 22), ("Hard", 22), ("Soft", 22)],
   [("Medium", 18), ("Hard", 30), ("Soft", 18)],
   [("Hard", 22), ("Soft", 22), ("Medium", 22)],
]


strategy_results = []
for strategy in strategy_pool:
   result = monte_carlo_simulation(verstappen, strategy)
   avg_time = np.mean(result)
   strategy_results.append((strategy, avg_time))


strategy_results.sort(key=lambda x: x[1])
best_strategy, best_time = strategy_results[0]


# ----------------- VISUALIZATION -------------------
labels = [f"{s[0][0]}-{s[1][0]}-{s[2][0]}" for s, _ in strategy_results]
times = [t for _, t in strategy_results]


plt.figure(figsize=(10, 5))
plt.bar(labels, times, color='purple')
plt.title("Average Race Time by 2-Stop Strategy")
plt.ylabel("Average Time (sec)")
plt.xlabel("Compound Strategy")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()


# Print best strategy
print("\nBest 2-Stop Strategy:")
for stint in best_strategy:
   print(f"{stint[0]} for {stint[1]} laps")
print(f"Average Race Time: {best_time:.2f} seconds")


