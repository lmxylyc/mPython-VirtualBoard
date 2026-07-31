oled.print("Press Button A")
while button_a.value() == 1:
    sleep_ms(50)
oled.print("Button A Pressed!")
rgb.fill((255, 255, 0))
rgb.write()
