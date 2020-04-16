# standard library
import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Button, Label, Checkbutton, Entry, filedialog
from tkinter.scrolledtext import ScrolledText
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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from tqdm import tqdm


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

# Main page inheriting from tk.Frame


class Application(tk.Frame):
    # Constructor
    def __init__(self, master=None):
        # master = root = main window
        super().__init__(master)
        # set master
        self.master = master
        # Set main window size
        self.master.geometry("900x1000+0+0")
        # Set window title
        self.master.winfo_toplevel().title("Lindemann Index Calculator")
        # Create all the widgets()
        self.create_widgets()
        # put all the widget in the designated grid
        self.grid()


# Create the widgets (Buttons, Labels, scrollable texts)


    def create_widgets(self):
        # Buttons
        # Button to import files
        self.file_button = Button(self,
                                  text="file list",
                                  command=self.get_filelist,
                                  width=15,)

        # button to extract number from file name
        self.num_button = Button(self,
                                 text="number list",
                                 command=self.get_numlist,
                                 width=15,
                                 state='disabled')
        # Button to compute lindemann index
        self.compute_button = Button(self,
                                     text="compute",
                                     command=self.compute,
                                     width=20,
                                     state='disabled')

        # button to quit the GUI
        self.quit_button = Button(self,
                                  text="QUIT",
                                  fg="red",
                                  command=self.quit,
                                  width=20,)
        # Button to reset the window
        self.clear_button = Button(self,
                                   text="Clear",
                                   command=self.clear,
                                   width=20,)

        # Button for plotting
        self.plot_button = Button(self,
                                  text="Plot",
                                  command=self.plot,
                                  width=20,)
        # state='disabled')

    # Labels
        # Label for file names
        self.file_label = Label(self,
                                text="Target Files",
                                width=15,)

        # label for numbers
        self.num_label = Label(self,
                               text="Numbers",
                               width=15,)

        # label for computed lindemann indexes
        self.compute_label = Label(self,
                                   text="Lindemann Index",
                                   width=15,)

        # Scrolled Text (File list, number list, Lindemann Index)
        # Text for file names
        self.file_text = ScrolledText(self,
                                      width=25,
                                      height=10,)
        # Text for number lists
        self.num_text = ScrolledText(self,
                                     width=20,
                                     height=10,)
        # Text for lindemann indexes
        self.compute_text = ScrolledText(self,
                                         width=20,
                                         height=10,)

    # Progerss bar
        # Progress bar max value and length
        self.bar_value = 500
        # Label for progress bar for each individual calculation
        self.bar_label = Label(self,
                               text="Computation Progress",
                               anchor="e",
                               width=20,)
        # Progress bar for each lindemann index calculation progress
        self.compute_bar = Progressbar(self,
                                       length=self.bar_value,
                                       maximum=self.bar_value,
                                       mode="determinate",
                                       value=0,)
        # Label for Progress bar for each file progress
        self.filebar_label = Label(self,
                                   text="File Progress",
                                   anchor="e",
                                   width=20,)
        # Progress bar for each lindemann index calculation
        self.filebar = Progressbar(self,
                                   length=self.bar_value,
                                   maximum=self.bar_value,
                                   mode="determinate",
                                   value=0,)

        # Showing how many files are left
        self.filecount_label = Label(self,
                                     text="file count: 0",
                                     anchor='w',
                                     width="10",)

        # Scrolled Text for logging
        self.log_label = Label(self,
                               text="log output",
                               width="60",)
        self.log_text = ScrolledText(self,
                                     width=60,
                                     height=10,)

    # Entry
        # Entry for file extension
        self.extension_label = Label(self,
                                     text="file extension:",
                                     anchor='e',
                                     width="10",)
        self.extension_entry = Entry(self)
        # default text value for the extension
        self.extension_entry.insert('end', '.lammpstrj')

        # Entry for file extension
        self.prefix_label = Label(self,
                                  text="File prefix:",
                                  anchor='e',
                                  width="10",)
        self.prefix_entry = Entry(self)
        # default text value for the prefix is "", hence no need to deifne

    # file explorer
        # label for current working directory
        self.cwd_label = Label(self,
                               text='Directory:',
                               anchor='e',
                               width='10',)

        # entry for current working directory
        self.cwd_entry = Entry(self)
        self.cwd_entry.insert('end', os.getcwd())
        # button for opening file explorer
        self.cwd_button = Button(self,
                                  text="get",
                                  command=self.browse_files,
                                  width=15,)

    # Placement
        # Placement of those buttons
        self.file_button.grid(column=0, row=0, sticky="we",)
        self.num_button.grid(column=1, row=0, sticky="we",)
        self.compute_button.grid(column=2, row=0, sticky="we",)
        self.quit_button.grid(column=3, row=0, sticky="we",)
        self.clear_button.grid(column=0, row=5, sticky="we",)

        # Placement of those labels
        self.file_label.grid(column=0, row=1, sticky="we",)
        self.num_label.grid(column=1, row=1, sticky="we",)
        self.compute_label.grid(column=2, row=1, sticky="we",)

        # Placement of those scrolled texts
        self.file_text.grid(column=0, row=2, sticky="we",)
        self.num_text.grid(column=1, row=2, sticky="we",)
        self.compute_text.grid(column=2, row=2, sticky="we",)

        # Placement of progress bar and labels
        self.bar_label.grid(column=0, row=3, sticky="we",)
        self.compute_bar.grid(column=1, row=3, columnspan=2, sticky="we",)
        self.filebar_label.grid(column=0, row=4, sticky="we",)
        self.filebar.grid(column=1, row=4, columnspan=2, sticky="we",)
        self.filecount_label.grid(column=3, row=4, sticky="we",)

        # Placement of log scroleld text and label
        self.log_label.grid(column=0, row=6, columnspan=3, sticky="we",)
        self.log_text.grid(column=0, row=7, columnspan=3, sticky="we",)

        # Placement of entry
        self.extension_label.grid(column=0, row=8, sticky="we",)
        self.extension_entry.grid(column=1, row=8, sticky="we",)
        self.prefix_label.grid(column=0, row=9, sticky="we",)
        self.prefix_entry.grid(column=1, row=9, sticky="we",)

        # Placement of plot
        self.plot_button.grid(column=0, row=10, sticky="we",)

        # Placement of cwd
        self.cwd_label.grid(column=0, row=11, sticky="we",)
        self.cwd_entry.grid(column=1, row=11, sticky="we",)
        self.cwd_button.grid(column=2, row=11, sticky="we",)

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

    def change_state(self, button, state):
        if state == 'on':
            button['state'] = 'normal'
        elif state == 'off':
            button['state'] = 'disabled'

    def get_filelist(self, file_prefix=""):
        # Turn off the file button to so user don't click until cleared
        self.change_state(self.file_button, 'off')

        # grab file_extension from the entry
        file_extension = self.extension_entry.get()

        # grab file_prefix from the entry
        file_prefix = self.prefix_entry.get()

        # initialize file list
        self.file_list = []
        # Log the current file extension to the GUI
        if file_extension == "":
            self.log_text.insert(
                tk.INSERT, 'No file extension was selected.\n')
        else:
            self.log_text.insert(
                tk.INSERT, f'Using "{file_extension}" as target file extension.\n')
        # log the current file prefix to the GUI
        if file_prefix == "":
            self.log_text.insert(
                tk.INSERT, 'No file prefix was selected.\n')
        else:
            self.log_text.insert(
                tk.INSERT, f'Using "{file_prefix}" as target file extension.\n')
        # First, get all the directories
        all_directory = os.listdir()
        # Extract only the one that is file, and file extension and file prefix(if given)
        for file in all_directory:
            if osp.isfile(file) and file.endswith(file_extension) and file.startswith(file_prefix):
                self.file_list.append(file)
        # Sort file naturally based on number in the file
        self.file_list = nt.natsorted(self.file_list)
        # Log the output
        self.log_text.insert(
            tk.INSERT, f'Found the lists of files')
        # insert the file into the scrolled text
        for file in self.file_list:
            self.file_text.insert(tk.INSERT, f'{file}\n')

        # Log the output
        self.log_text.insert(
            tk.INSERT, f'...........outputted.\n')

        # Update the file count for progress bar
        self.filecount_label["text"] = f"file count: {len(self.file_list)}"

        # Turn on the number and compute button to allow user clicking
        self.change_state(self.num_button, 'on')
        self.change_state(self.compute_button, 'on')

# Get the number from file name (Ex. nano3_573K.lammpstrj, then get 573)
    def get_numlist(self):
        # Turn off num button so user do not click again
        self.change_state(self.num_button, 'off')

        # initialize the number list
        self.num_list = []
        # Log the file extension to the GUI
        self.log_text.insert(
            tk.INSERT, '\nFinding the list of numbers associated to the file name......\n')

        # iterate each file
        for file in self.file_list:
            # Regular expression to find the number from files
            # slicing([1:-1]) is used because the result is nested list,
            # and the [] and '' are not needed when outputting
            number = str(re.findall(r'\d+', file))[1:-1]
            self.num_list.append(number)
        # sort the list
        self.num_list = nt.natsorted(self.num_list)

        # log the file that is
        self.log_text.insert(
            tk.INSERT, 'Found the lists of numbers')
        # Slicing again to remove the another [] and '' symbol
        # Then output to the scrolled text box
        for number in self.num_list:
            number = str(number)[1:-1]
            self.num_text.insert(tk.INSERT, f'{number}\n')

        # log the file that is
        self.log_text.insert(tk.INSERT, '......outputted.\n')

    # Resetting the window
    def clear(self):
        # Reset the scrolled text by deleting the content
        self.file_text.delete("1.0", "end")
        self.num_text.delete("1.0", "end")
        self.compute_text.delete("1.0", "end")
        self.log_text.delete("1.0", "end")

        # Reset the progress bar
        self.compute_bar['value'] = 0
        self.filebar['value'] = 0
        self.filecount_label['text'] = "file count: 0"

        # Change the button state
        self.change_state(self.file_button, 'on')
        self.change_state(self.num_button, 'off')
        self.change_state(self.compute_button, 'off')
        self.change_state(self.quit_button, 'on')

    # Save the value to a file
    def save_value(self, file_name='Lindemann.txt'):

        with open(file_name, 'w') as write_file:
            write_file.write('Lindemann Index is \n')
        for count, file in enumerate(self.file_list):
            with open('Lindemann.txt', 'a+') as write_file:
                LI = np.array2string(self.lindemann_index_cluster[count])
                output = '{}\n'.format(LI)
                write_file.write(f"{file}:{LI} \n")

    # Plot the result: Lindemann index vs temperature
    def plot(self):
        figure = plt.Figure()
        ax1 = figure.add_subplot(111)
        scatter1 = FigureCanvasTkAgg(figure, self)
        ax1.plot(self.lindemann_index_cluster)
        # scatter1.show()
        scatter1.get_tk_widget().grid(column=0, row=11, columnspan=6, sticky="we",)

    def browse_files(self):
        # self.filename = filedialog.askopenfilename(initialdir = "/",
        # title = "Select a File",
        # filetypes = (("Text files", "*.txt*"),("all files", "*.*")),)
        self.filepath = filedialog.askdirectory()
        self.cwd_entry.insert('end', self.filepath)



    # Calculating the Lindemann Index
    def compute(self):
        # Turn off compute button so user do not compute again
        self.change_state(self.compute_button, 'off')
        # Turn off quit button so user cannot quit in the middle of computation
        self.change_state(self.quit_button, 'off')
        # Initializing
        self.lindemann_index_cluster = np.zeros(len(self.file_list))
        # For each file
        for count, file in enumerate(self.file_list):
            # Initializing the each compute brogress bar
            self.compute_bar['value'] = 0
            # Initializign the file count
            self.filecount_label['text'] = f"file count: {count+1}/{len(self.file_list)}"
            self.update_idletasks()
            # logging to scrolled text
            self.log_text.insert(
                tk.INSERT, f"\nCalculating the Lindemann Index for: {file}\n")

            # tracking elapsed time
            t_start = time.time()

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
            # Example: diff will calculate atom1-2, atom2-3,atom3-4, and so on
            difference = np.diff(position, axis=0)  # position axis = 0

            #   LI calculation
            for k in range(num_distance):
                # position axis = 0, xyz axis = 1, time axis = 2.
                position_axis = 0
                xyz_axis = 1
                time_axis = 2
                # cumsum to obtain cumulative sum of the differences
                # if the number is 1, 2, 3, 4
                # Cumsum will give 1, 3, 6, 10
                # Adding 1-2, 2-3, will give 1-3
                # Adding 1,2, 2-3, 3-4, will give 1-4
                # atom1-2, atom1-3, atom1-4, atom1-5 and so on
                xyz = np.cumsum(difference[k:, :, :], axis=position_axis)
                # Square each and sum up and take sqrt based on distance formula
                distance = np.sqrt(np.sum(xyz**2, xyz_axis))
                # due to the sum function, now the time axis = 1 and coordinate axis disappear
                time_axis = 1
                # Take the time average
                distance_average[k:, k] = np.mean(distance, axis=time_axis)
                # Take the squared time average
                distance_square_average[k:, k] = np.mean(
                    distance**2, axis=time_axis)
                # For progress bar for each computation
                self.compute_bar['value'] = self.compute_bar['value'] + \
                    self.bar_value / num_distance
                self.update_idletasks()

            # Calculate the coefficient
            coefficient = 2 / ((num_particle) * (num_particle - 1))
            # Square the time-averaged distance
            distance_average_square = distance_average[:]**2
            # supprsessing 0 division error warning
            with np.errstate(divide='ignore', invalid='ignore'):
                lindemann_index_individual = np.sqrt(
                    distance_square_average - distance_average_square) / distance_average
            # Since half of the matrix is division by 0, there will be NaN
            # Hence conversion to 0 is necessary.
            lindemann_index_individual = np.nan_to_num(
                lindemann_index_individual[:])
            # Store the final value into matrix so we can obtain all at once later
            self.lindemann_index_cluster[count] = coefficient * \
                np.sum(lindemann_index_individual)

            # To calculate the elapsed time
            calc_time = time.time() - t_start

            # outputting lindeman index to lindemann scrolled text
            self.compute_text.insert(
                tk.INSERT, f'{self.lindemann_index_cluster[count]}\n')
            # logging elapsed time
            self.log_text.insert(
                tk.INSERT, f"Elapsed time: {calc_time}\n\n")
            # Autoscroll the scrolled bar
            self.log_text.see('end')
            # Update the progress bar for file progress
            self.filebar['value'] = self.filebar['value'] + \
                self.bar_value / len(self.file_list)
            self.update_idletasks()

        # Turn on quit button since the computation is done
        self.change_state(self.quit_button, 'on')


if __name__ == '__main__':
    main()
