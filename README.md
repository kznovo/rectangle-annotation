R(ectancle)annotation - Bounding box annotation tool
===============

**Rannotation** is a tool to annotate images with rectangular bounding boxes of multiple categories.


|  sample usage  |  description  |
| ----- | ----- |
|  ![example1](https://github.com/kznovo/rectangle-annotation/blob/master/sample/annotation_tool_sample_add_resize_move.gif)  |  - Add label with a click.<br>  - Use the markers around the label to resize.<br>  - Drag, or use "hjkl" keys to move the label.<br>  - Double click or press delete/d key to erase the active label<br>  |
|  ![example2](https://github.com/kznovo/rectangle-annotation/blob/master/sample/annotation_tool_sample_multilabel.gif)  |  - Active label appears as light green, while inactive label appears dark green.<br>  - You can edit the active label's coordinates and categories<br>  - Switch active label's category with number keys.<br>  - Switch active labels by tab key  |
|  ![example3](https://github.com/kznovo/rectangle-annotation/blob/master/sample/annotation_tool_sample_csv_resume.gif)  |  - All the changes made will be overwritten to the csv<br>  - The labels will be loaded from the csv from the next time the same image is opened  |



## Installation

```shell
pip install rannotation
```

## Usage

1. Prepare images in a directory.
2. Create a labelmap (json). Ex:

```json
[
    {
        "id": 1,
        "label": "Pedestrian"
    },
    {
        "id": 2,
        "label": "Car"
    },
    {
        "id": 3,
        "label": "Truck"
    },
    {
        "id": 4,
        "label": "Stopsign"
    }
]
```

3. Prepare a csv file. If it's the first time usage, **the tool will create a new csv file for you**. If you want to resume from the previous work, prepare the csv output from then.

4. Start with `rannotate` command with 3 arguments:

```shell
rannotate \
    --img_dir \
    --csv_path \
    --labelmap_path
```

- Mouse:

  - **Click on image** :           create new label OR deactivate labels  

  - **Click on a label** :         activate the label  

  - **Drag a label** :               move the label  

  - **Drag a marker** :             resize the label  

  - **Double click on a label** :  delete the label  



- Keys:

  - **Enter** :  Save  

  - **Tab** :    Activate a label / switch active labels

  - **Delete** or **d** : Delete active label  

  - **h** :      Move an active label a few steps left  

  - **j** :      Move an active label a few steps down  

  - **k** :      Move an active label a few steps up  

  - **l** :      Move an active label a few steps left  

  - **b** :      Go to the previous image OR activate the previous label  

  - **n** :      Go to the next image OR activate the next label  

  - **s** :      Show/hide labels  

  - **q** :      Quit app  

  - **1-9** :    Label category on the active label  

  - **i** :      Predict labels using the prediction model  



## Notes

- csv should contain the following fields:  
`['filename', 'obj_name', 'xmin', 'ymin', 'xmax', 'ymax']`  
If there's no csv file in the path then a new csv file will be created.

- Currently the tool only supports **up to 10 categories**.
