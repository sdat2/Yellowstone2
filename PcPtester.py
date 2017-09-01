from obspy.taup import TauPyModel
model = TauPyModel(model="prem")



for x in range(int(30/5),int(90/5)):
    x5 = x*5
    arrivals=model.get_travel_times(source_depth_in_km=55,distance_in_degree=x5,phase_list = ["P"])
    print('P at ',x5,'degrees is:\t', arrivals[0].time,' s')

for x in range(int(30/5),int(90/5)):
    arrivals=model.get_travel_times(source_depth_in_km=55,distance_in_degree=x*5,phase_list = ["PcP"])
    print('PcP at ',x*5,'degrees is:\t', arrivals[0].time,' s')

for x in range(int(30/5),int(90/5)):
    arrivals=model.get_travel_times(source_depth_in_km=55,distance_in_degree=x*5,phase_list = ["P"])
    arrivals1=model.get_travel_times(source_depth_in_km=55,distance_in_degree=x*5,phase_list = ["PcP"])
    print('Difference at ',x*5,'degrees is:\t', "{:.2f}".format(arrivals1[0].time - arrivals[0].time),' s')
    
