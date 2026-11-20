# jetbot_digitaltwin

Digitaler Zwilling des Waveshare JetBot für ROS 2 Jazzy. Der Roboter wird in RViz angezeigt
und kann per Tastatur gefahren werden.

## Starten

```bash
cd ~/ros2_ws
colcon build --packages-select jetbot_digitaltwin
source install/setup.bash
ros2 launch jetbot_digitaltwin display.launch.py
```

Fahren (zweites Terminal, vorher `source install/setup.bash`):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

`i` vorwärts, `j`/`l` drehen, `u`/`o` Kurve, `k` stopp.

## Aufbau

| Ordner / Datei | Inhalt |
|---|---|
| `urdf/jetbot.urdf.xacro` | Roboterbeschreibung (Maße aus dem CAD-Modell) |
| `meshes/` | STL-Teile pro Link (Chassis, Räder, Jetson, Kamera, …) |
| `src/motor_driver_node.py` | Motortreiber-Node (Differentialantrieb) |
| `launch/display.launch.py` | startet robot_state_publisher, Motortreiber und RViz |
| `rviz/jetbot.rviz` | gespeicherte RViz-Ansicht (Fixed Frame: `odom`) |

## Motortreiber

`motor_driver_node.py` empfängt Fahrbefehle und berechnet daraus Radwinkel und Position:

```
/cmd_vel (Twist) ──▶ motor_driver ──▶ /joint_states        (Radwinkel → Räder drehen sich)
                                 └──▶ TF odom → base_footprint (Position → Roboter fährt)
```

- Radradius: 0.0336 m, Radabstand: 0.1183 m
- Die Position wird per Odometrie aufsummiert (Startpunkt = `odom`).

## 3D-Modell

Das Modell stammt aus dem Waveshare-Wiki: https://www.waveshare.com/wiki/JetBot_AI_Kit
– dort unter Resourcen "JetBot 3D Drawing" (STEP-Datei, mit FreeCAD in STL-Teile zerlegt).

Fehlt eine der STL-Dateien in `meshes/`, zeigt RViz automatisch das eigene Box-Modell.
