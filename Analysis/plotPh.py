#!/usr/bin/env python
# coding: utf-8

# # Look at the pH of the system

# In[1]:


import os
import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
#%matplotlib inline

# In[2]:

start_time = time.time()
desktop_root_path = "/home/neil/"
desktop_windows_root_path = "C:\\Users\\neil"
pi_root_path = "/home/pi/"
if os.path.isdir(desktop_root_path):
    data_path = os.path.join(desktop_root_path,"growControl_Data")
    analysis_path = os.path.join(desktop_root_path,"growControl","Analysis")
elif os.path.isdir(desktop_windows_root_path):
    data_path = os.path.join(desktop_windows_root_path,"growControl_Data")
    analysis_path = os.path.join(desktop_windows_root_path,"growControl","Analysis")
elif os.path.isdir(pi_root_path):
    data_path = os.path.join(pi_root_path,"growControl_Data")
    analysis_path = os.path.join(pi_root_path,"growControl","Analysis")
else:
    raise FileNotFoundError("No valid path to the data was found!")


# In[3]:


data_files = {}
for d in os.listdir(data_path):
    if not os.path.isfile(os.path.join(data_path,d)):
        continue
    root = d[:d.rfind("_")]
    full_path = os.path.join(data_path,d)
    if root not in data_files:
        data_files[root] = [full_path]
    else:
        data_files[root].append(full_path)

print("Found all files after {:.1f} s".format(time.time()-start_time))

# In[4]:


def load_df(root_name):
    li = []
    for fname in sorted(data_files[root_name])[-10:]:
        df_temp = pd.read_csv(fname,index_col=None,header=0,skiprows=lambda x: (x!=0) and not x%10)
        li.append(df_temp)
    df = pd.concat(li,axis=0,ignore_index=True)


    df["datetime_timezone"] = pd.to_datetime(df["datetime_timezone"])
    df.sort_values("datetime_timezone",inplace=True)
    df.reset_index(inplace=True,drop=True)
    return df
df_ph = load_df("sensor_ph_bin1")
df_control_ph = load_df("controller_ph_pump")

print("Loaded ph and control data after {:.1f} s".format(time.time()-start_time))
# In[5]:


#df_ph["ph_avg_ewm_.1"] = df_ph["ph_raw"].ewm(adjust=False,alpha=.1).mean()
#df_ph["ph_avg_ewm_.01"] = df_ph["ph_raw"].ewm(adjust=False,alpha=.01).mean()
#df_ph["ph_avg_ewm_.001"] = df_ph["ph_raw"].ewm(adjust=False,alpha=.001).mean()

#print("Computed moving averages after {:.1f} s".format(time.time()-start_time))
# In[7]:


#plt.rcParams["figure.figsize"] = (50,25)
plt.rcParams["figure.figsize"] = (20,10)
fig, ax1 = plt.subplots()
ax1.set_xlabel("Date")
ax1.set_ylabel("pH")

ax1.plot(df_ph["datetime_timezone"],df_ph["ph_raw"],label="raw")
ax1.plot(df_ph["datetime_timezone"],df_ph["ph_avg"],label="ph_avg")

#ax1.plot(df_ph["datetime_timezone"],df_ph["ph_avg_ewm_.1"],label="average_factor=0.9")
#ax1.plot(df_ph["datetime_timezone"],df_ph["ph_avg_ewm_.01"],label="average_factor=0.99")
#ax1.plot(df_ph["datetime_timezone"],df_ph["ph_avg_ewm_.001"],label="average_factor=0.999")

datetime_minmax = [df_ph["datetime_timezone"].min(),df_ph["datetime_timezone"].max()]
ax1.plot(datetime_minmax,[6.0,6.0],label="pH Min")
ax1.plot(datetime_minmax,[6.2,6.2],label="pH Max")

ax1.legend(loc="upper left")
ax1.minorticks_on()
ax1.grid(True,which="major",linewidth=1)
ax1.grid(True,which="minor",linewidth=.5)
plt.ylim((4.5,8.))
plt.xlim(datetime_minmax)

ax2 = ax1.twinx()
ax2.set_ylabel("pH Adjustment Volume\n[ml]")
ax2.bar(df_control_ph["datetime_timezone"],df_control_ph["ph_down_volume"],width=.01,alpha=.2,label="pH Down")
ax2.bar(df_control_ph["datetime_timezone"],df_control_ph["ph_up_volume"],width=.01,alpha=.2,label="pH Up")
ax2.legend(loc="upper right")
plt.ylim((0,2.0))
plt.xlim(datetime_minmax)
print("Created plot after {:.1f} s".format(time.time()-start_time))
plt.savefig(os.path.join(analysis_path,"ph_data_{}.png".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))))
print("Saved plot after {:.1f} s".format(time.time()-start_time))
plt.show()
print("Completed in {:.1f} s".format(time.time()-start_time))








# %%
