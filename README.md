# Darknet for Collision Avoidance

This project is for detecting intruder planes as in advance as possible to avoid the collision very efficiently in order to use less fuel. This can be related to **small object detection**. And I have solved this issue with Yolov4 trained with simulation images and cockpit videos in Youtube. My solution may seem simple and straightforward. However, it works well. 

---

## Commands
### Train
- with single gpu  
`./darknet detector train <.data> <.cfg> <weights> -map -dont_show -show_image -clear`
- with multi gpus  
`./darknet detector train <.data> <.cfg> <weights> -map -gpus 0,1,2,3 -dont_show -show_image -clear`

### Test (demo) 
- images  
`./darknet detector test <.data> <.cfg> <weights> -thresh 0.25`
- video  
`./darknet detector demo <.data> <.cfg> <weights> <.mp4> -dont_show -out_filename <.avi>`
- webcam  
`./darknet detector demo <.data> <.cfg> <weights> -c 0`

### Options
| Arg | Description |
| :--- | :--- |
| `-dont_show` | Do not show the results in the new window |
| `-out_filename <outputfile>` | Save results in jpg, mp4, or avi |
| `-ext_output` | Log the pixels of bboxes |
| `-json_port <port>` | Open the json server and stream results |
| `-mjpeg_port <port>` | Open the mjpeg server and stream results |

### More Informations
Check more infos of usage at [the original repo](https://github.com/AlexeyAB/darknet).

## Datasets Used in This Project
| Name | Descriptions |
| :--- | :--- |
| `simulations` | Images obtained from the plane-crash simulation. Thank to (랩이름) |
| Youtube | | 
## Weights
## DEMOs