# Make spirograph hypotrochoid curves in Abaqus
- `ComputeSpirograph.py` builds a two-bar system which computes spirograph hypotrochoid curves.
- `PostProcessSpirograph.py` draws spirograph hypotrochoid curves.

## Model Setup
Refer to [blog post](http://yaor.me/spirographs-in-abaqus/).
## Usage
1. Modify and run `ComputeSpirograph.py` to produce ODB result file.
2. Modify and run `PostProcessSpirograph.py` to draw spirograph curves.

When the boolean flag `writePNG` in `PostProcessSpirograph.py` is set to `True`, the script outputs a series of PNGs that can be used to make animation GIF, refer to this [workflow](http://yaor.me/make-gifs-from-abaqus/).

## Test
The scripts are developed and tested in Abaqus 6.14-4.