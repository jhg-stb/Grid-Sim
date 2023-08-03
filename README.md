# Grid-Sim

## Input File Format

### Vehicles Mobility Data
The mobility data for vehicles should be provided in the following format:

| Date         | Time     | Latitude        | Longitude     | Altitude | Speed   | Distance* |
| -------------| ---------| --------------- | --------------| ---------| --------|--------|
| yyyy-mm-dd   | hh:mm:ss | [degrees]       | [degrees]     | [meters] | [km/h]  | [meters] |

*Note: *The Distance column is optional. If you are not including Distance, please do not create this column in your input file.*

### External Batteries
The input format of the solar PV data should be exactly as given by SAM (System Advisor Model). To use this data, ensure the file is saved in the correct directory with the name "Solar_Information.csv."

---

The units and format of all other input parameters required are described in the input file, which is automatically generated when the scenario is initialized.

## Usage

For examples of how to use Grid-Sim and a more in-depth explanation of the software, please refer to the papers written with this software available at the following links:

1. [https://doi.org/10.36227/techrxiv.23544567.v1](https://doi.org/10.36227/techrxiv.23544567.v1)
2. [https://dx.doi.org/10.2139/ssrn.4497144](https://dx.doi.org/10.2139/ssrn.4497144)

## Contact Information

For more information about this software or any inquiries, feel free to contact me at jhgiliomee@sun.ac.za. I am happy to assist and provide support with the usage and implementation of Grid-Sim.










