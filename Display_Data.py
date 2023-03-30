import pandas as pd
import matplotlib.pyplot as plt
import os

# Set the directory path where the CSV files are located
directory = r'E:\Masters\Grid_Sim\Paper\Results\Individual_Battery_Results\Reference\Power'

# Loop through all the CSV files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        # Read the CSV file into a pandas dataframe
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath)
        
        # Set the index to columns 2-11 and plot the data
        ax = df.iloc[:, 1:11].set_index(df.iloc[:, 0]).plot(linewidth=4)
        
        # Set y-axis limit, title, and x-axis title
        ax.set_ylim([0, 1250])
        ax.set_ylabel('Power [kW]', fontsize=17)
        ax.set_xlabel('Hour of The Day [h]', fontsize=17)
        
        # Change x-axis to hours and display every hour as tick
        ax.set_xticks(range(0, 1441, 60))
        ax.set_xticklabels([f'{i//60}:00' for i in range(0, 1441, 60)], rotation='vertical', fontsize=12)
        
        # Increase font size of x and y-axis labels and tick labels
        plt.xticks(fontsize=17)
        plt.yticks(fontsize=17)
        ax.xaxis.label.set_size(17)
        ax.yaxis.label.set_size(17)
        ax.legend(fontsize=15)
        #ax.legend(fontsize=15, loc='lower left', bbox_to_anchor=(0, 0))
        
        # Remove the plot title and save the plot in the same directory as the CSV file
        ax.set_title('')
        plot_title = os.path.splitext(filename)[0]
        plt.savefig(os.path.join(directory, f'{plot_title}.png'), dpi=300)

        # Set the minimum and maximum x-axis limits such that the first data point is right on the y-axis
        ax.set_xlim(df.iloc[0, 0] - 30, df.iloc[-1, 0] + 30)

        #plt.plot([0, 1440], [20, 20], '--', color='black')

        # Adjust subplot parameters to remove spaces on both sides of the x-axis within the plot window
        plt.tight_layout()
        
        # Show the plot
        plt.show()


