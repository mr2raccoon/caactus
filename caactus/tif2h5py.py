# -*- coding: utf-8 -*-
"""
Created on Thu May 16 10:51:17 2024

@author: q243js
"""
# Import the imagecodecs package for handling image compression
import imagecodecs

# Import necessary standard libraries and packages
import os             # Provides functions for interacting with the operating system
import tifffile       # Library for reading and writing TIFF files
import h5py           # Library for working with HDF5 files
import vigra          # Library for image processing and analysis

# Function to get the input directory path from the user
def get_input_directory():
    return input("Enter the directory path of the original tif-files to be imported: ")

# Function to get the output directory path from the user
def get_output_directory():
    return input("Enter the directory path where the .h5-files should be saved: ")

# Function to convert TIFF files to HDF5 files
def convert_tif_to_h5(input_dir, output_dir):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get a list of all TIFF files in the input folder
    tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]

    for tif_file in tif_files:
        tif_path = os.path.join(input_dir, tif_file)
        with tifffile.TiffFile(tif_path) as tiff:
            image_data = tiff.asarray()  # Read image data from the TIFF file
            num_dimensions = len(image_data.shape)  # Get the number of dimensions in the image
            
            print("Image data shape:", image_data.shape)  # Print the shape of the image data

            # Reshape the image data to include dimensions for t and z
            if num_dimensions == 3:
                image_data_5d = image_data.reshape((1, 1, *image_data.shape))
            elif num_dimensions == 4:
                image_data_5d = image_data.reshape((1, *image_data.shape))
            else:
                image_data_5d = image_data.shape
                
            data_shape = image_data_5d.shape  # Store the shape of the reshaped data

            # Generate axistags in the "tzyxc" format
            axistags = vigra.defaultAxistags("tzyxc")

            # Create corresponding HDF5 file
            h5_file = os.path.splitext(tif_file)[0] + '.h5'  # Generate the HDF5 file name
            h5_path = os.path.join(output_dir, h5_file)  # Get the full path of the HDF5 file

            # Write image data to HDF5 file
            with h5py.File(h5_path, 'w') as h5:
                ds = h5.create_dataset(name='data', data=image_data_5d, chunks=(1, 1, 256, 256, 1))  # Create dataset
                ds.attrs["axistags"] = axistags.toJSON()  # Store axistags as attribute
                ds.attrs["data_shape"] = data_shape  # Store data shape as attribute

        # Print a message indicating successful conversion
        print(f"Converted {tif_file} to {h5_file}")

# Main block: Entry point of the script
if __name__ == "__main__":
    # Get the input and output directory paths from the user
    input_dir = get_input_directory()
    output_dir = get_output_directory()

    # Call the function to convert TIFF files to HDF5 files
    convert_tif_to_h5(input_dir, output_dir)

