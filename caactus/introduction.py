DESCRIPTION = """
<images/ascii-art-text.png>

## Welcome to caactus

**caactus** (cell analysis and counting tool using ilastik software) is a collection of Python scripts providing a streamlined workflow for ilastik (https://www.ilastik.org/).

It covers data preparation, image processing, and statistical analysis, giving biologists an easy-to-use tool for counting and classifying cells across large microscopy datasets.

## How to use this interface

### 1. Set your Main Folder
Enter the **full path** to your project directory at the top. All sub-folders follow the fixed naming convention described in the README.

### 2. Configure Global Settings
Set **Pixel Size**, **Variable Names**, **Class Order**, and **Color Mapping** once. They are shared across all analysis steps. For EUCAST datasets, expand the **EUCAST Settings** section.

### 3. Choose a Mode
Use the **Mode** selector (`training` / `batch`) to switch all workflow steps at once.

### 4. Follow the Workflow
Click **? Help** next to any step for detailed instructions. Steps marked **Ilastik** require work in the ilastik application — click **? Help** for step-by-step guidance.

## Folder structure

All sub-folder names correspond to the fixed structure of your main project directory. Default names can be overridden per-step via the **Advanced paths** section under each step.

For full documentation and the sample dataset, see the project README on GitHub.
"""