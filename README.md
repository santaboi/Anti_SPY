# Synopsys Portable enemy detection system
## Synopsys ARC Iotdk board
[Synopsys board documents](https://www.synopsys.com/dw/ipdir.php?ds=arc_iot_development_kit)
## Demonstration to the system
![](https://i.imgur.com/cS8X8A7.png)
[demonstration.pdf](https://github.com/santaboi/Anti_SPY/blob/main/Anti_SPY.pdf)
## INTRO
+ pragramming on Synopsys ARC IOTdk board
+ face classification is opencv based
+ signal passing to BC using UARC
## System flowchart
![](https://i.imgur.com/GCE7OSt.png)

## Face Classification
+ known_face_encoding : contain every unenemy
![](https://i.imgur.com/L8kieN2.png)
+ if any people's face appear in PC camerae , signal passing to ARC Iotdk board and alarm system go off
