for %%f in (*.png) do (
    ffmpeg -i "%%f" -vf format=rgba,scale=-2:108 temp.png
    move /Y temp.png "%%f"
)

pause