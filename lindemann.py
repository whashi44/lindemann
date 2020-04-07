# standard library
import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Button, Label, Checkbutton, scrolledtext
import os
import os.path as osp
import sys
import re
import time

# external library
import numpy as np
import natsort as nt
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier
# from tqdm import tqdm


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


class Application(tk.Frame):
    def __init__(self, master=None):
        # master = root = main window
        super().__init__(master)
        self.master = master
        self.master.geometry("900x1000")
        self.master.winfo_toplevel().title("Lindemann Index Calculator")
        self.pack()
        self.create_widgets()

    # Create the widgets (Buttons, Labels, scrollable texts)
    def create_widgets(self):
        # Buttons
        self.file_button = Button(self,
                                  text="file list",
                                  command=self.get_filelist,
                                  width=20,)

        self.num_button = Button(self,
                                 text="number list",
                                 command=self.get_numlist,
                                 width=20,)

        self.compute_button = Button(self,
                                     text="compute",
                                     command=self.compute,
                                     width=20,)
        self.quit_button = Button(self,
                                  text="QUIT",
                                  fg="red",
                                  command=self.quit,
                                  width=20,)
        self.clear_button = Button(self,
                                   text="Clear",
                                   command=self.clear,
                                   width=20,)

        self.file_button.grid(column=0, row=0, sticky="we",)
        self.num_button.grid(column=1, row=0, sticky="we",)
        self.compute_button.grid(column=2, row=0, sticky="we",)
        self.quit_button.grid(column=3, row=0, sticky="we",)

        # Labels
        self.file_label = Label(self,
                                text="Target Files",
                                width="25",)
        self.num_label = Label(self,
                               text="Numbers",
                               width="20",)
        self.compute_label = Label(self,
                                   text="Lindemann Index",
                                   width="20",)

        self.file_label.grid(column=0, row=1, sticky="we",)
        self.num_label.grid(column=1, row=1, sticky="we",)
        self.compute_label.grid(column=2, row=1, sticky="we",)
        self.clear_button.grid(column=0, row=5, sticky="we",)

        # Scrolled Text (File list, number list, Lindemann Index)
        self.file_text = scrolledtext.ScrolledText(self,
                                                   width=25,
                                                   height=10,)
        self.num_text = scrolledtext.ScrolledText(self,
                                                  width=20,
                                                  height=10,)
        self.compute_text = scrolledtext.ScrolledText(self,
                                                      width=20,
                                                      height=10,)
        self.file_text.grid(column=0, row=2, sticky="we",)
        self.num_text.grid(column=1, row=2, sticky="we",)
        self.compute_text.grid(column=2, row=2, sticky="we",)

        # Progerss bar
        self.bar_value = 500
        self.bar_label = Label(self,
                               text="Computation Progress",
                               anchor="e",
                               width="20",)

        self.bar = Progressbar(self,
                               length=self.bar_value,
                               maximum=self.bar_value,
                               mode="determinate",
                               value=0,)

        self.filebar_label = Label(self,
                                   text="File Progress",
                                   anchor="e",
                                   width="20",)

        self.filebar = Progressbar(self,
                                   length=self.bar_value,
                                   maximum=self.bar_value,
                                   mode="determinate",
                                   value=0,)

        self.filecount_label = Label(self,
                                     text="file count: 0",
                                     anchor='w',
                                     width="10",)

        self.bar_label.grid(column=0, row=3, sticky="we",)
        self.bar.grid(column=1, row=3, columnspan=2, sticky="we",)
        self.filebar_label.grid(column=0, row=4, sticky="we",)
        self.filebar.grid(column=1, row=4, columnspan=2, sticky="we",)
        self.filecount_label.grid(column=3, row=4, sticky="we",)

        # Scrolled Text (Log)
        self.log_label = Label(self,
                               text="log output",
                               width="60",)
        self.log_text = scrolledtext.ScrolledText(self,
                                                  width=60,
                                                  height=10,)
        self.log_label.grid(column=0, row=6, columnspan=3, sticky="we",)
        self.log_text.grid(column=0, row=7, columnspan=3, sticky="we",)

        #
        # self.chk_state = tk.BooleanVar()
        # self.chk_state.set(False)
        # self.chk = Checkbutton(self, text="Test", var=self.chk_state)
        # self.chk.grid(column=0, row=6)
        #
        # self.rad1 = tk.Radiobutton(self, text="First", value=1)
        # self.rad2 = tk.Radiobutton(self, text="Second", value=2)
        # self.rad3 = tk.Radiobutton(self, text="Third", value=3)
        # self.rad1.grid(column=0,row=7)
        # self.rad2.grid(column=1,row=7)
        # self.rad3.grid(column=2,row=7)
    # Get the list of file from the directories with specified file extension
    def get_filelist(self, file_prefix="", file_extension='.lammpstrj'):
        self.file_list = []
        # Log the file extension to the GUI
        self.log_text.insert(
            tk.INSERT, f'Using "{file_extension}" as target file extension........\n')
        # First, get all the directories
        all_directory = os.listdir()
        # Extract only the one with file_extension
        for file in all_directory:
            if osp.isfile(file) and file.endswith(file_extension) and file.startswith(file_prefix):
                self.file_list.append(file)
        # Sort file naturally
        self.file_list = nt.natsorted(self.file_list)
        # Log the output
        self.log_text.insert(
            tk.INSERT, f'Found the lists of files.....outputted.\n')
        for file in self.file_list:
            self.file_text.insert(tk.INSERT, f'{file}\n')
        # Update the file count for progress bar
        self.filecount_label["text"] = f"file count: {len(self.file_list)}"

    # Get the number from file name (Ex. nano_573K.lammpstrj, then get 573)
    def get_numlist(self):
        self.num_list = []
        # Log the file extension to the GUI
        self.log_text.insert(
            tk.INSERT, f'Finding the list of numbers associated to the file name......\n')
        for file in self.file_list:
            # Regular expression to find the number from files
            # slicing is used because the result is nested list,
            # and the [] and '' are not needed when outputting
            number = str(re.findall(r'\d+', file))[1:-1]
            self.num_list.append(number)
        self.num_list = nt.natsorted(self.num_list)

        self.log_text.insert(
            tk.INSERT, f'Found the lists of numbers......outputted. \n')
        # Slicing again to remove the another [] and '' symbol
        # Then output to the scrolled text box
        for number in self.num_list:
            number = str(number)[1:-1]
            self.num_text.insert(tk.INSERT, f'{number}\n')

    # Resetting the window
    def clear(self):
        # Reset the scrolled text
        self.file_text.delete("1.0", "end")
        self.num_text.delete("1.0", "end")
        self.compute_text.delete("1.0", "end")
        self.log_text.delete("1.0", "end")

        # Reset the progress bar
        self.bar['value'] = 0
        self.filebar['value'] = 0
        self.filecount_label['text'] = "file count: 0"

    # Save the value to a file
    def save_value(self):
        with open('Lindemann.txt', 'w') as write_file:
            write_file.write('Lindemann Index is \n')
        for count, file in enumerate(self.file_list):
            with open('Lindemann.txt', 'a+') as write_file:
                LI = np.array2string(self.LindemannIndex_cluster[count])
                output = '{}\n'.format(LI)
                write_file.write(f"{file}:{LI} \n")

    # Plot the result: Lindemann index vs temperature
    def plot_value(self):
        pass

    # Calculating the Lindemann Index
    def compute(self):
        # file_extension = input('Enter the desired file extension: ')

        self.LindemannIndex_cluster = np.zeros(len(self.file_list))
        # For each file
        for count, file in enumerate(self.file_list):
            # For outputting
            self.bar['value'] = 0
            self.filecount_label['text'] = f"file count: {count+1}/{len(self.file_list)}"
            self.update_idletasks()
            self.log_text.insert(
                tk.INSERT, f"Calculating the Lindemann Index for: {file}\n")

            t = time.time()

            # Importing the files
            pipeline = import_file(file, sort_particles=True)
            num_frame = pipeline.source.num_frames
            # Choosing specific atom type for future usage
            pipeline.modifiers.append(
                SelectTypeModifier(operate_on="particles",
                                   property="Particle Type",
                                   types={1, 2, 3}))
            data = pipeline.compute()

            #   Initilizations
            num_particle = data.particles.count
            num_distance = num_particle - 1
            distance = np.zeros((num_distance, num_frame))
            distance_average = np.zeros((num_distance, num_distance))
            distance_square_average = np.zeros((num_distance, num_distance))
            position = np.zeros(((num_particle, 3, num_frame)))
            # Store particle position into a single matrix
            for frame in range(num_frame):
                data = pipeline.compute(frame)
                position[:, :, frame] = np.array(data.particles['Position'])
            # Calculate the difference between each consecutive atom for later usage
            # Example: diff will calculate atom1-atom2, atom2-atom3,atom3-atom4, and so on
            difference = np.diff(position, axis=0)  # position axis = 0

            #   LI calculation
            # for k in tqdm(range(num_distance), desc='Calculation'):
            for k in range(num_distance):
                # position axis = 0, xyz axis = 1, time axis = 2.
                position_axis = 0
                xyz_axis = 1
                time_axis = 2
                # cumsum to add the difference so you get
                # atom1-2, atom1-3, atom1-4, atom1-5 and so on
                xyz = np.cumsum(difference[k:, :, :], axis=position_axis)
                # Square each and sum up and take sqrt based on distance formula
                distance = np.sqrt(np.sum(xyz**2, xyz_axis))

                # due to the sum function, now the time axis = 1 and coordinate axis disappear
                time_axis = 1
                # Take the time average
                distance_average[k:, k] = np.mean(distance, axis=time_axis)
                # Take the squared time average
                distance_square_average[k:, k] = np.mean(distance**2, axis=time_axis)
                # For progress bar

                self.bar['value'] = self.bar['value'] + \
                    self.bar_value / num_distance
                self.update_idletasks()

            # Calculate the coefficient
            coefficient = 2 / ((num_particle) * (num_particle - 1))
            # Square the time-averaged distance
            distance_average_square = distance_average[:]**2
            # supprsessing 0 division error warning
            with np.errstate(divide='ignore', invalid='ignore'):
                LindemannIndex_individual = np.sqrt(
                    distance_square_average - distance_average_square) / distance_average
            # Since half of the matrix is division by 0, there will be NaN
            # Hence conversion to 0 is necessary.
            LindemannIndex_individual = np.nan_to_num(
                LindemannIndex_individual[:])
            # Store the final value into matrix so we can obtain all at once later
            self.LindemannIndex_cluster[count] = coefficient * \
                np.sum(LindemannIndex_individual)

            calc_time = time.time() - t

            # Logging purpose
            self.compute_text.insert(
                tk.INSERT, f'{self.LindemannIndex_cluster[count]}\n')
            self.log_text.insert(
                tk.INSERT, f"Elapsed time: {calc_time}\n")
            self.filebar['value'] = self.filebar['value'] + \
                self.bar_value / len(self.file_list)
            self.update_idletasks()

if __name__ == '__main__':
    main()
