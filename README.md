# Darknet for Collision Avoidance

## Commands
### Train
`./darknet detector train <.data> <.cfg> <weights> -map -gpus 0,1,2,3 -dont_show -show_image -clear`

### Test (demo) 
- images  
`./darknet detector test <.data> <.cfg> <weights> -thresh 0.25`
- video  
`./darknet detector demo <.data> <.cfg> <weights> <.mp4> -dont_show -out_filename <.avi>`
- webcam  
`./darknet detector demo <.data> <.cfg> <weights> -c 0`

### Options

`-dont_show`: 실행 결과를 새 창으로 보이지 않음  
`-out_filename <outputfile>`: 실행 결과를 영상으로 저장  
`-ext_output`: box들의 좌푯값을 로깅  
`-json_port <port>`: json 서버에 결과 값을 스트림  
`-mjpeg_port <port>`: mjpeg 서버에 결과 값을 스트림

## Datasets
## Weights
## DEMOs