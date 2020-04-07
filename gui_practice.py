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
# from tqdm import tqdm
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


class Application(tk.Frame):
    def __init__(self, master=None):
        # master = root = main window
        super().__init__(master)
        # self.file_list = []
        # self.num_list = []
        self.master = master
        self.master.geometry("900x1000")
        self.master.winfo_toplevel().title("Lindemann Index Calculator")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.file_button = Button(self,
                                  text="file list",
                                  command=self.get_filelist,
                                  justify="left",
                                  width=20,)
        self.file_button.grid(column=0, row=0, sticky="we",)

        self.num_button = Button(self,
                                 text="number list",
                                 command=self.get_numlist,
                                 justify="left",
                                 width=20,)
        self.num_button.grid(column=1, row=0, sticky="we",)

        self.compute_button = Button(self,
                                     text="compute",
                                     command=self.compute,
                                     justify="left",
                                     width=20,)
        self.compute_button.grid(column=2, row=0, sticky="we",)

        self.quit_button = Button(self,
                                  text="QUIT",
                                  fg="red",
                                  command=self.quit,
                                  justify="left",
                                  width=20,)
        self.quit_button.grid(column=3, row=0, sticky="we",)

        self.file_label = Label(self,
                                text="Target Files",
                                justify="left",
                                width="25",)
        self.file_label.grid(column=0, row=1, sticky="we",)
        self.num_label = Label(self,
                               text="Numbers",
                               justify="left",
                               width="20",)
        self.num_label.grid(column=1, row=1, sticky="we",)
        self.compute_label = Label(self,
                                   text="Lindemann Index",
                                   justify="left",
                                   width="20",)
        self.compute_label.grid(column=2, row=1, sticky="we",)

        self.file_text = scrolledtext.ScrolledText(self,
                                                   width=25,
                                                   height=10,)
        self.file_text.grid(column=0, row=2, sticky="we",)
        self.num_text = scrolledtext.ScrolledText(self,
                                                  width=20,
                                                  height=10,)
        self.num_text.grid(column=1, row=2, sticky="we",)
        self.compute_text = scrolledtext.ScrolledText(self,
                                                      width=20,
                                                      height=10,)
        self.compute_text.grid(column=2, row=2, sticky="we",)

        self.bar_label = Label(self,
                               text="Computation Progress",
                               anchor="e",
                               width="20",)
        self.bar_label.grid(column=0, row=3, sticky="we",)

        self.bar_value = 500
        self.bar = Progressbar(self,
                               length=self.bar_value,
                               maximum=self.bar_value,
                               mode="determinate",
                               value=0,)
        self.bar.grid(column=1, row=3, columnspan=2, sticky="we",)

        self.filebar_label = Label(self,
                                   text="File Progress",
                                   anchor="e",
                                   width="20",)
        self.filebar_label.grid(column=0, row=4, sticky="we",)

        self.filebar = Progressbar(self,
                                   length=self.bar_value,
                                   maximum=self.bar_value,
                                   mode="determinate",
                                   value=0,)
        self.filebar.grid(column=1, row=4, columnspan=2, sticky="we",)

        self.filecount_label = Label(self,
                                     text="file count: 0",
                                     anchor='w',
                                     width="10",)
        self.filecount_label.grid(column=3, row=4, sticky="we",)

        self.clear_button = Button(self,
                                   text="Clear",
                                   command=self.clear,
                                   justify="left",
                                   width=20,)
        self.clear_button.grid(column=0, row=5, sticky="we",)

        self.log_label = Label(self,
                               text="log output",
                               width="60",)
        self.log_label.grid(column=0, row=6, columnspan=3, sticky="we",)

        self.log_text = scrolledtext.ScrolledText(self,
                                                  width=60,
                                                  height=10,)
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

    def get_filelist(self, file_prefix="", file_extension='.lammpstrj'):
        self.file_list = []
        self.log_text.insert(
            tk.INSERT, f'Using "{file_extension}" as target file extension........\n')

        all_directory = os.listdir()
        for file in all_directory:
            if osp.isfile(file) and file.endswith(file_extension) and file.startswith(file_prefix):
                self.file_list.append(file)
        self.file_list = nt.natsorted(self.file_list)
        self.log_text.insert(
            tk.INSERT, f'Found the lists of files.....outputted.\n')
        for file in self.file_list:
            self.file_text.insert(tk.INSERT, f'{file}\n')
        self.filecount_label["text"] = f"file count: {len(self.file_list)}"

    def get_numlist(self):
        self.num_list = []
        self.log_text.insert(
            tk.INSERT, f'Finding the list of numbers associated to the file name......\n')

        for file in self.file_list:
            number = str(re.findall(r'\d+', file))[1:-1]
            # re for getting number from file name
            self.num_list.append(number)
        self.num_list = nt.natsorted(self.num_list)

        self.log_text.insert(
            tk.INSERT, f'Found the lists of numbers......outputted. \n')

        for number in self.num_list:
            number = str(number)[1:-1]
            self.num_text.insert(tk.INSERT, f'{number}\n')

    def clear(self):
        self.file_text.delete("1.0", "end")
        self.num_text.delete("1.0", "end")
        self.compute_text.delete("1.0", "end")
        self.log_text.delete("1.0", "end")
        self.bar['value'] = 0
        self.filebar['value'] = 0
        self.filecount_label['text'] = "file count: 0"

    def save_value(self):
        with open('Lindemann.txt', 'w') as write_file:
            write_file.write('Lindemann Index is \n')
        for count, file in enumerate(self.file_list):
            with open('Lindemann.txt', 'a+') as write_file:
                LI = np.array2string(self.LindemannIndex_cluster[count])
                output = '{}\n'.format(LI)
                write_file.write(f"{file}:{LI} \n")

    def plot_value(self):
        pass

    def compute(self):
        # file_extension = input('Enter the desired file extension: ')
        #   Initialize txt file

        self.LindemannIndex_cluster = np.zeros(len(self.file_list))
        for count, file in enumerate(self.file_list):
            self.bar['value'] = 0
            self.filecount_label['text'] = f"file count: {count+1}/{len(self.file_list)}"
            self.update_idletasks()

            t = time.time()
            self.log_text.insert(
                tk.INSERT, f"Calculating the Lindemann Index for: {file}\n")
            #   importing the files
            pipeline = import_file(file, sort_particles=True)
            num_frame = pipeline.source.num_frames
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
            for frame in range(num_frame):
                data = pipeline.compute(frame)
                position[:, :, frame] = np.array(data.particles['Position'])
            difference = np.diff(position, axis=0)  # position axis = 0

            #   LI calculation
            # for k in tqdm(range(num_distance), desc='Calculation'):
            for k in range(num_distance):
                # position axis = 0
                xyz = np.cumsum(difference[k:, :, :], axis=0)
                # coordinate axis = 0
                distance = np.sqrt(np.sum(xyz**2, axis=1))
                # due to the sum function, now the time axis = 1
                distance_average[k:, k] = np.mean(distance, axis=1)
                distance_square_average[k:, k] = np.mean(distance**2, axis=1)
                self.bar['value'] = self.bar['value'] + \
                    self.bar_value / num_distance
                self.update_idletasks()
            coefficient = 2 / ((num_particle) * (num_particle - 1))
            distance_average_square = distance_average[:]**2
            # supprsessing 0 division error warning
            with np.errstate(divide='ignore', invalid='ignore'):
                LindemannIndex_individual = np.sqrt(
                    distance_square_average - distance_average_square) / distance_average
            LindemannIndex_individual = np.nan_to_num(
                LindemannIndex_individual[:])
            self.LindemannIndex_cluster[count] = coefficient * \
                np.sum(LindemannIndex_individual)

            calc_time = time.time() - t

            self.compute_text.insert(
                tk.INSERT, f'{self.LindemannIndex_cluster[count]}\n')
            self.log_text.insert(
                tk.INSERT, f"Elapsed time: {calc_time}\n")
            self.filebar['value'] = self.filebar['value'] + \
                self.bar_value / len(self.file_list)
            self.update_idletasks()


if __name__ == '__main__':
    main()
