colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
for c in colors:
    for i in range(3):
        rgb[i] = c
    rgb.write()
    sleep_ms(300)
