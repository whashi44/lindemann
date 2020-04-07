"""
    This function calculates the Lindemann Index based on the
    given files
    The flow of the function is as follows
    1. Read the file in the directory
    2. Select the file with specific extension
    3. Read the content of teh file
    4. Extract atom coordinates
    5. Calculate the Lindemann Index
"""

#standard library
import os,sys,re,time
import os.path as osp
from pprint import pprint

# pip packages
import numpy as np
import natsort as nt
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier
import tqdm



# get the list of file in the directory that meet the criteria
def get_filelist(file_extension='.lammpstrj'):
    file_list = []
    file_prefix = 'nano3'
    print(f'Using {file_extension} as target file extension')
    all_directory = os.listdir()

    for file in all_directory:
        if osp.isfile(file) and file.endswith(file_extension):
        # if osp.isfile(file) and file.endswith(file_extension) and file.startswith(file_prefix):
            file_list.append(file)
    file_list = nt.natsorted(file_list)
    return file_list

def get_numlist(file_list):
    num_list = []
    for file in file_list:
            num_list.append(re.findall(r'\d+', file)) #re for getting number from file name
    num_list = nt.natsorted(num_list)
    return num_list

def calc_lindex():
    # file_extension = input('Enter the desired file extension: ')
    file_list = get_filelist()
    print(f'Found the lists of files {file_list}')
    num_list = get_numlist(file_list)

    #   Initialize txt file
    with open('Lindemann.txt','w') as write_file:
        write_file.write('Lindemann Index is \n')

    #   Initialize lindemann index value
    LindemannIndex_cluster = np.zeros(len(file_list))

    for count,file in enumerate(file_list):
        t = time.time()
        print(f"Calculating the Lindemann Index for file {file}")
        #   importing the files
        pipeline = import_file(file, sort_particles=True)
        num_frame = pipeline.source.num_frames
        pipeline.modifiers.append(SelectTypeModifier(
            operate_on = "particles",
            property = "Particle Type",
            types = {1,2,3}
        ))
        data = pipeline.compute()
        #   Initilizations
        num_particle = data.particles.count
        num_distance = num_particle - 1
        distance = np.zeros((num_distance,num_frame))
        distance_average = np.zeros((num_distance,num_distance))
        distance_square_average = np.zeros((num_distance,num_distance))
        position = np.zeros(((num_particle,3,num_frame)))
        for frame in range(num_frame):
            data = pipeline.compute(frame)
            position[:,:,frame] = np.array(data.particles['Position'])
        difference = np.diff(position,axis = 0) #position axis = 0

        #   LI calculation
        for k in tqdm.tqdm(range(num_distance), desc = 'Calculation'):
            xyz = np.cumsum(difference[k:,:,:],axis=0)  #position axis = 0
            distance = np.sqrt(np.sum(xyz**2,axis = 1))  #coordinate axis = 0
            distance_average[k:,k] = np.mean(distance, axis = 1) #due to the sum function, now the time axis = 1
            distance_square_average[k:,k] = np.mean(distance**2, axis = 1)
        coefficient = 2 / ((num_particle) * (num_particle - 1))
        distance_average_square = distance_average[:]**2
        with np.errstate(divide='ignore', invalid='ignore'): #supprsessing 0 division error warning
            LindemannIndex_individual = np.sqrt(distance_square_average - distance_average_square) / distance_average
        LindemannIndex_individual = np.nan_to_num(LindemannIndex_individual[:])
        LindemannIndex_cluster[count] = coefficient * np.sum(LindemannIndex_individual)

        calc_time = time.time() - t

        with open('Lindemann.txt','a+') as write_file:
            LI =np.array2string(LindemannIndex_cluster[count])
            output = '{}\n'.format(LI)
            write_file.write(f"{file}:{LI} \n")

        print(f"LindemannIndex for set temperature file: {file} is: {LindemannIndex_cluster[count]} \n") #* to print as space instead pf ['']
        print(f"Elapsed time is {calc_time}")
# ----------Scan and Store file ----------------
def main():
    calc_lindex()
#   Useful for debugging
# np.savetxt('test.txt',position[:,:,0])
# np.savetxt('Lindemann.txt',LindemannIndex_cluster)

if __name__ =='__main__':
    main()
