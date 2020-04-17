# standard library
import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Button, Label, Checkbutton, Entry, filedialog, Radiobutton
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
    """Main application class to create tkinter window
    """

    # -------------------------------------------------------------------------------
    def __init__(self, master=None):
        """Constructor to initialize
        """
        # master = root = main window
        super().__init__(master)
        # set master
        self.master = master
        # Set main window size, and +0+0 indicate the x location and y location
        self.master.geometry("900x1000+0+0")
        # Set window title
        self.master.winfo_toplevel().title("Lindemann Index Calculator")
        # Create all the widgets()
        self.create_widgets()
        # Initialize tha path
        self.filepath = os.getcwd()
        # put all the widget in the designated grid
        self.pack()

    # -------------------------------------------------------------------------------
    def create_widgets(self):
        """ create the widgets, i.e. buttons, labels, scrolled text, check button, radio button
        """
        # --------Buttons---------
        # Button to import files
        self.file_button = Button(
            self, text="file list", command=self.get_filelist, width=15,
        )

        # button to extract number from file name
        self.num_button = Button(
            self,
            # disabled unless users import file
            text="number list",
            command=self.get_numlist,
            width=15,
            state="disabled",
        )
        # Button to compute lindemann index
        # disabled unless users import file
        self.compute_button = Button(
            self, text="compute", command=self.compute, width=20, state="disabled"
        )

        # button to quit the GUI
        self.quit_button = Button(
            self, text="QUIT", fg="red", command=self.quit, width=20,
        )
        # Button to reset the window
        self.clear_button = Button(self, text="Clear", command=self.clear, width=20,)

        # Button for plotting
        self.plot_button = Button(
            self, text="Plot", command=self.plot, state="disabled", width=20,
        )
        # state='disabled')

        # --------Labels---------
        # Label for file names
        self.file_label = Label(self, text="Target Files", width=15,)

        # label for numbers
        self.num_label = Label(self, text="Numbers", width=15,)

        # label for computed lindemann indexes
        self.compute_label = Label(self, text="Lindemann Index", width=15,)

        # --------Scrolled Text---------
        # Text for file names
        self.file_text = ScrolledText(self, width=25, height=10,)
        # Text for number lists
        self.num_text = ScrolledText(self, width=20, height=10,)
        # Text for lindemann indexes
        self.compute_text = ScrolledText(self, width=20, height=10,)

        # --------Progerss bar---------
        # Progress bar max value and length
        self.bar_value = 500
        # Label for progress bar for each individual calculation
        self.bar_label = Label(self, text="Computation Progress", anchor="e", width=20,)

        # Progress bar for each lindemann index calculation progress
        self.compute_bar = Progressbar(
            self,
            length=self.bar_value,
            maximum=self.bar_value,
            mode="determinate",
            value=0,
        )

        # Label for Progress bar for each file progress
        self.filebar_label = Label(self, text="File Progress", anchor="e", width=20,)

        # Progress bar for each lindemann index calculation
        self.filebar = Progressbar(
            self,
            length=self.bar_value,
            maximum=self.bar_value,
            mode="determinate",
            value=0,
        )

        # Showing how many files are left
        self.filecount_label = Label(
            self, text="file count: 0", anchor="w", width="10",
        )

        # --------Logging---------
        # Scrolled Text for logging
        self.log_label = Label(self, text="log output", width="60",)

        self.log_text = ScrolledText(self, width=60, height=10,)

        # --------Entry---------
        # Entry for file extension
        self.extension_label = Label(
            self, text="file extension:", anchor="e", width="10",
        )
        self.extension_entry = Entry(self)

        # default text value for the extension
        self.extension_entry.insert("end", ".lammpstrj")

        # Entry for file extension
        self.prefix_label = Label(self, text="File prefix:", anchor="e", width="10",)
        self.prefix_entry = Entry(self)
        # default text value for the prefix is "", hence no need to redefine

        # --------Filedialog---------
        # label for current working directory
        self.cwd_label = Label(self, text="Directory Name:", anchor="e", width="10",)

        # entry for current working directory
        self.cwd_entry = Entry(self)
        self.cwd_entry.insert("end", os.getcwd())

        # button for opening file explorer to open directory
        self.cwd_button = Button(
            self, text="Browse", command=self.browse_folder, width=15,
        )

        # button for saving the content to a file
        self.save_button = Button(
            self, text="Save to file", command=self.save, width=15, state='disabled'
        )
        # --------Check button---------
        # check button for choosing to use num_list for graphing or not
        self.chk_state = tk.BooleanVar()
        self.chk_state.set(False)
        self.numlist_check = Checkbutton(
            self, text="Use numbers list as x-axis", var=self.chk_state
        )

        # --------Radio button---------
        # Radio button to choose batch file reading vs. single file reading
        # Creating string variable for tkinter
        self.chk_batch_single = tk.StringVar()
        # Initializing to batch mode
        self.chk_batch_single.set("batch")
        self.batch = Radiobutton(
            self, text="batch", variable=self.chk_batch_single, value="batch",
        )
        self.single = Radiobutton(
            self, text="single", variable=self.chk_batch_single, value="single",
        )

        # --------------------Placement----------------
        # Buttons

        self.file_button.grid(
            column=0, row=0, sticky="we",
        )
        self.num_button.grid(
            column=1, row=0, sticky="we",
        )
        self.compute_button.grid(
            column=2, row=0, sticky="we",
        )
        self.quit_button.grid(
            column=3, row=0, sticky="we",
        )
        self.clear_button.grid(
            column=0, row=5, sticky="we",
        )

        # Labels
        self.file_label.grid(
            column=0, row=1, sticky="we",
        )
        self.num_label.grid(
            column=1, row=1, sticky="we",
        )
        self.compute_label.grid(
            column=2, row=1, sticky="we",
        )

        # Scrolled texts
        self.file_text.grid(
            column=0, row=2, sticky="we",
        )
        self.num_text.grid(
            column=1, row=2, sticky="we",
        )
        self.compute_text.grid(
            column=2, row=2, sticky="we",
        )

        # Progress bar and labels
        self.bar_label.grid(
            column=0, row=3, sticky="we",
        )
        self.compute_bar.grid(
            column=1, row=3, columnspan=2, sticky="we",
        )
        self.filebar_label.grid(
            column=0, row=4, sticky="we",
        )
        self.filebar.grid(
            column=1, row=4, columnspan=2, sticky="we",
        )
        self.filecount_label.grid(
            column=3, row=4, sticky="we",
        )

        # Log scroleld text and label
        self.log_label.grid(
            column=0, row=6, columnspan=3, sticky="we",
        )
        self.log_text.grid(
            column=0, row=7, columnspan=3, sticky="we",
        )

        # Entry
        self.extension_label.grid(
            column=0, row=8, sticky="we",
        )
        self.extension_entry.grid(
            column=1, row=8, sticky="we",
        )
        self.prefix_label.grid(
            column=0, row=9, sticky="we",
        )
        self.prefix_entry.grid(
            column=1, row=9, sticky="we",
        )

        # Plot button
        self.plot_button.grid(
            column=0, row=10, sticky="we",
        )

        # Placement of open directory
        self.cwd_label.grid(
            column=0, row=11, sticky="we",
        )
        self.cwd_entry.grid(
            column=1, row=11, columnspan=2, sticky="we",
        )
        self.cwd_button.grid(
            column=3, row=11, sticky="we",
        )

        # Placement of save button
        self.save_button.grid(
            column=0, row=12, sticky="we",
        )

        # Placement of Checkbutton
        self.numlist_check.grid(
            column=0, row=13, sticky="we",
        )

        # Placement of Radio button
        self.batch.grid(column=0, row=14)
        self.single.grid(column=1, row=14)

    # -------------------------------------------------------------------------------
    # Change the state of button to a given state (on or off)

    def change_state(self, button, state):
        """Change the state of button to a given state

        Args:
            button (object): button object that needs change in state
            state (string): "on" or "off"

        Example
        change_state(self.button, "on")
        will turn on the self.button
        """
        if state == "on":
            button["state"] = "normal"
        elif state == "off":
            button["state"] = "disabled"

    # -------------------------------------------------------------------------------

    def get_filelist(self):
        """Get the list of file from the directories with specified file extension and specified file prefix
        """
        # Turn off the file button so user don't click until cleared
        self.change_state(self.file_button, "off")

        # grab file_extension from the entry
        file_extension = self.extension_entry.get()

        # grab file_prefix from the entry
        file_prefix = self.prefix_entry.get()

        # initialize file list
        self.file_list = []
        # Log the current file extension to the GUI
        if file_extension == "":
            self.log_text.insert(tk.INSERT, "No file extension was selected.\n")
        else:
            self.log_text.insert(
                tk.INSERT, f'Using "{file_extension}" as target file extension.\n'
            )
        # log the current file prefix to the GUI
        if file_prefix == "":
            self.log_text.insert(tk.INSERT, "No file prefix was selected.\n")
        else:
            self.log_text.insert(
                tk.INSERT, f'Using "{file_prefix}" as target file prefix.\n'
            )
        # First, get all the directories
        all_directory = os.listdir()

        # Extract only the one that is file, and file extension and file prefix(if given)
        for file in all_directory:
            if (
                osp.isfile(file)
                and file.endswith(file_extension)
                and file.startswith(file_prefix)
            ):
                self.file_list.append(file)
        # Sort file naturally based on number in the file
        self.file_list = nt.natsorted(self.file_list)
        # Log the output
        self.log_text.insert(tk.INSERT, f"Outputting the lists of files to the console")
        # insert the file into the scrolled text
        for file in self.file_list:
            self.file_text.insert(tk.INSERT, f"{file}\n")

        # Log the output
        self.log_text.insert(tk.INSERT, f"...........outputted.\n")

        # Update the file count for progress bar
        self.filecount_label["text"] = f"file count: {len(self.file_list)}"

        # Turn on the number and compute button to allow user to click button
        self.change_state(self.num_button, "on")
        self.change_state(self.compute_button, "on")

    # -------------------------------------------------------------------------------
    # Get the number from file name (Ex. nano3_573K.lammpstrj, then get 573)

    def get_numlist(self):
        """Extract the number from file name
        Ex. if the file name is prod_573K.lammpstrj,
        This function will extract 573 and append to num_list
        """
        # Turn off num button so user do not click again
        self.change_state(self.num_button, "off")

        # initialize the number list
        self.num_list = []
        # Log the file extension to the GUI
        self.log_text.insert(
            tk.INSERT, "\nExtracting of numbers from the list of file names......\n"
        )

        # iterate each file
        for file in self.file_list:
            # Regular expression to find the number from files
            # Since the findall return the list, it is necessary to obtain the 0th element
            # The result is string, so convert it to int
            number = int(re.findall(r"\d+", file)[0])
            self.num_list.append(number)
            # log to the scrolled text
            self.num_text.insert(tk.INSERT, f"{number}\n")

        # log
        self.log_text.insert(tk.INSERT, "Extracted the numbers from the file name")

    # -------------------------------------------------------------------------------
    def clear(self):
        """Reset the window
        """
        # Reset the scrolled text by deleting the content
        self.file_text.delete("1.0", "end")
        self.num_text.delete("1.0", "end")
        self.compute_text.delete("1.0", "end")
        self.log_text.delete("1.0", "end")

        # Reset the progress bar
        self.compute_bar["value"] = 0
        self.filebar["value"] = 0
        self.filecount_label["text"] = "file count: 0"

        # Change the button state
        self.change_state(self.file_button, "on")
        self.change_state(self.quit_button, "on")
        self.change_state(self.num_button, "off")
        self.change_state(self.compute_button, "off")
        self.change_state(self.save_button, "off")
        self.change_state(self.plot_button, "off")


    # -------------------------------------------------------------------------------
    def save(self):
        """Save the value to a file
        It will prompt user a directory to save a file
        The default file format it txt file
        """
        # file types for the dialog
        files = [("All Files", "*.*"), ("Text Files", "*.txt")]
        # return file name. If canceled, return blank string
        file_name = filedialog.asksaveasfilename(
            initialdir=self.filepath,
            filetypes=files,
            defaultextension="*.txt",
            initialfile="lindemann.txt",
        )
        # check for user cancel
        if file_name != "":
            # open the text file
            with open(file_name, "w") as write_file:
                # iterate through file name from file list
                for count, file in enumerate(self.file_list):
                    # too long for the f string, so store in temp variable
                    LI = self.lindemann_index_cluster[count]
                    # output = '{}\n'.format(LI)
                    write_file.write(f"{file}:{LI} \n")

            # log
            self.log_text.insert(
                tk.INSERT, f"Lindemann index value was save to the file: {file_name}\n"
            )
        else:
            self.log_text.insert(
                tk.INSERT, "File save cancelled\n"
            )

    # -------------------------------------------------------------------------------
    def plot(self):
        """Plot the result
        If the check button was pressed, then the lindemann index vs. num_list will be plot
        If the check was not pressed, then the lindemann index will be plotted against some consecutive numbers
        """
        figure = plt.Figure()
        ax1 = figure.add_subplot(111)
        scatter1 = FigureCanvasTkAgg(figure, self)
        if self.chk_state:
            ax1.plot(self.num_list, self.lindemann_index_cluster)
        else:
            ax1.plot(self.lindemann_index_cluster)
        # scatter1.show()
        scatter1.get_tk_widget().grid(
            column=0, row=11, columnspan=6, sticky="we",
        )

    # -------------------------------------------------------------------------------
    def browse_folder(self):
        """ Prompt user to open a directory and change the current directory to that folder
        """
        # Obtaint the file path
        temp_path = filedialog.askdirectory(initialdir=self.filepath)
        # If user did not cancel the dialog
        if temp_path:
            self.filepath = temp_path
            # Clear the entry
            self.cwd_entry.delete(0, "end")
            # insert the new file path
            self.cwd_entry.insert("end", self.filepath)
            # Change the directory to a specified path
            os.chdir(self.filepath)

            # log
            self.log_text.insert(tk.INSERT, f"Changed the directory to {self.filepath}\n")
        else:
            # log
            self.log_text.insert(tk.INSERT, "Cancelled directory change\n")


    # -------------------------------------------------------------------------------

    def compute(self):
        """Calculate the lindemann index
        """
        # Turn off compute button so user do not compute again
        self.change_state(self.compute_button, "off")
        # Turn off quit button so user cannot quit in the middle of computation
        self.change_state(self.quit_button, "off")
        # Initializing
        self.lindemann_index_cluster = np.zeros(len(self.file_list))
        # For each file
        for count, file in enumerate(self.file_list):
            # Initializing the each compute brogress bar
            self.compute_bar["value"] = 0
            self.update_idletasks()
            # logging to scrolled text
            self.log_text.insert(
                tk.INSERT, f"\nCalculating the Lindemann Index for: {file}\n"
            )

            # tracking elapsed time
            t_start = time.time()

            # Importing the files
            pipeline = import_file(file, sort_particles=True)
            num_frame = pipeline.source.num_frames
            # Choosing specific atom type for future usage
            pipeline.modifiers.append(
                SelectTypeModifier(
                    operate_on="particles", property="Particle Type", types={1, 2, 3}
                )
            )
            data = pipeline.compute()

            #   Initilizations
            num_particle = data.particles.count
            num_distance = num_particle - 1
            distance = np.zeros((num_distance, num_frame))
            distance_average = np.zeros((num_distance, num_distance))
            distance_square_average = np.zeros((num_distance, num_distance))
            position = np.zeros(((num_particle, 3, num_frame)))
            # Store particle position into a single matrix
            # The matrix dimension is as follows:
            # 1st: The coordinates position, i.e. 1.0, 3.0, 4.0
            # 2nd: The coordiante axis: i.e. x, y or z
            # 3rd: The time axis: i.e. timestep 0, timestep 1,....
            for frame in range(num_frame):
                data = pipeline.compute(frame)
                position[:, :, frame] = np.array(data.particles["Position"])

            # Calculate the difference between each consecutive atom for later usage
            # Example: diff will calculate the difference between
            # atom1-2, atom2-3,atom3-4, and so on
            position_axis = 0
            difference = np.diff(position, axis=position_axis)

            #   Lindemann index calculation
            # for each individual atom, starting from 0,
            # k increment every time, because the calculation will be performed for
            # Atom 1-2, 1-3, ....1-n, and then 2-3, 2-4,.....2-n and so on
            for k in range(num_distance):
                xyz_axis = 1
                time_axis = 2
                # cumsum to obtain the cumulative sum of the differences
                # if the number is 1, 2, 3, 4
                # Cumsum will give 1, 3, 6, 10
                # Adding 1-2, 2-3, will give 1-2, 1-3
                # Adding 1,2, 2-3, 3-4, will give 1-2, 1-3, 1-4
                # atom1-2, atom1-3, atom1-4, atom1-5 and so on
                xyz = np.cumsum(difference[k:, :, :], axis=position_axis)
                # Square each and sum up and take sqrt based on distance formula
                distance = np.sqrt(np.sum(xyz ** 2, xyz_axis))
                # due to the sum function, now the time axis = 1 and coordinate axis disappear
                time_axis = 1
                # Take the time-average
                distance_average[k:, k] = np.mean(distance, axis=time_axis)
                # Take the time-average of the squared distance
                distance_square_average[k:, k] = np.mean(distance ** 2, axis=time_axis)
                # For progress bar for each computation
                self.compute_bar["value"] = (
                    self.compute_bar["value"] + self.bar_value / num_distance
                )
                self.update_idletasks()

            # Calculate the coefficient
            coefficient = 2 / ((num_particle) * (num_particle - 1))
            # Take the square of time-averaged distance
            distance_average_square = distance_average[:] ** 2
            # supprsessing 0 division error warning
            with np.errstate(divide="ignore", invalid="ignore"):
                lindemann_index_individual = (
                    np.sqrt(distance_square_average - distance_average_square)
                    / distance_average
                )
            # Since half of the matrix is division by 0, there will be NaN
            # Hence conversion from NaN to 0 is necessary.
            lindemann_index_individual = np.nan_to_num(lindemann_index_individual[:])
            # Sum up all the individual lindeman index to obtain lindemann index cluster
            # Store the final value into matrix so we can obtain all at once later
            self.lindemann_index_cluster[count] = coefficient * np.sum(
                lindemann_index_individual
            )

            # To calculate the elapsed time
            calc_time = time.time() - t_start

            # outputting lindeman index to lindemann scrolled text
            self.compute_text.insert(
                tk.INSERT, f"{self.lindemann_index_cluster[count]}\n"
            )
            # logging elapsed time
            self.log_text.insert(tk.INSERT, f"Elapsed time: {calc_time}\n\n")
            # Update the progress bar for file progress
            self.filebar["value"] = self.filebar["value"] + self.bar_value / len(
                self.file_list
            )
            # Update the file count
            self.filecount_label[
                "text"
            ] = f"file count: {count+1}/{len(self.file_list)}"
            self.update_idletasks()

            # Autoscroll the scrolled text
            self.log_text.see("end")
            self.compute_text.see("end")


        # Turn on quit button since the computation is done
        self.change_state(self.quit_button, "on")
        self.change_state(self.plot_button, "on")
        self.change_state(self.save_button, "on")


if __name__ == "__main__":
    main()
