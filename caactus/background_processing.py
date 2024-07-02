# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 08:30:06 2024

@author: q243js
"""

import os  # Import the os module for interacting with the operating system
import h5py  # Import h5py for handling HDF5 files
import numpy as np  # Import NumPy for numerical operations

def process_image(image_path):
    """
    Process a single HDF5 image file by modifying its 'exported_data' dataset.

    Parameters:
    image_path (str): Path to the HDF5 image file.

    Raises:
    KeyError: If the dataset 'exported_data' does not exist in the file.
    """
    try:
        # Open the image using h5py in read/write mode
        with h5py.File(image_path, 'r+') as img:
            # Check if 'exported_data' exists in the file
            if 'exported_data' not in img:
                raise KeyError(f"The dataset 'exported_data' does not exist in {image_path}")

            # Convert the image to a NumPy array
            image = np.array(img['exported_data'])
        
            # Find unique IDs and their counts
            ids, counts = np.unique(image, return_counts=True)
        
            # Find the largest ID
            largest_id = ids[counts.argmax()]
        
            # Set pixels with the largest ID to zero
            image[image == largest_id] = 0

            # Update the 'exported_data' dataset in the HDF5 file with the modified image
            img['exported_data'][:] = image
    except Exception as e:
        print(f"Error processing file {image_path}: {str(e)}")

def get_input_directory():
    """
    Prompt the user to enter the directory path of pictures to be analyzed.

    Returns:
    str: The input directory path entered by the user.
    """
    return input("Enter the directory path of pictures to be analyzed: ")

def batch_process_images(input_directory):
    """
    Process all HDF5 image files in the given directory.

    Parameters:
    input_directory (str): Path to the directory containing HDF5 image files.
    """
    # Process each image in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith("Segmentation.h5"):
            input_path = os.path.join(input_directory, filename)
            
            # Print the input path for debugging
            print(f"Processing file: {input_path}")
            
            # Process the image
            process_image(input_path)

            print(f"Processed {filename} and updated in-place.")

if __name__ == "__main__":
    # Get the input directory from the user
    input_dir = get_input_directory()

    # Call the batch_process_images function with the user-provided directory
    batch_process_images(input_dir)