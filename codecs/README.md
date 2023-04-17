# Programs
[FFmpeg](https://ffmpeg.org)

# Container
Use `mkv` (more widely supported) or `nut` (can contain more less used codecs) since they are open formats.

# Video

## Lossy
* Software: `libsvtav1`
  * Quality control: `-crf`. Range: `1-63`. Default `0` (automatic).
  * Speed control: `-preset`. Range: `0-13`. Default: `-1` (automatic), seems like `10`.
* Hardware: `av1_nvenc` if available (from 4000 series). Else `hevc_nvenc`.
  * Quality control: `-cq`. Range: `1-51`. Default: `0` (automatic).
  * Speed control: `-preset`. Range: `p1-p7`. Default: `p4`.

* Notes:
  * For compatibility, use `libx264` instead of `libx265` and `libvpx-vp9`, as the `libx264` encoder is more optimised in FFmpeg than the others. Just tune its speed and quality control.
    * Quality control: `-crf`. Range: `0-3.40282e+38`. Default: `23`
    * Speed control: `-preset`. Range: `placebo-ultrafast`. Default: `medium`

## Lossless
Try to use the same colour format as the source, since RGB to YUV 4:4:4 8-bit is lossy.

For RGB:
* Software: `libx264rgb`: `-qp 0`. 
  * Speed control: `-preset`. Range: `placebo-ultrafast`. Default: `medium`.
    * For even faster speed than `ultrafast`, try `ffv1` and `huffyuv`.
* Hardware: `av1_nvenc`: `-pix_fmt gbrp -tune lossless`.
  * Speed control: Same as above


# Audio

## Lossy
* Software: `libopus`
  * Speed control: `-compression_level`. Range: `0-10`. Default: `10`.

## Lossless
* Software: `flac`
  * Speed control: `-compression_level`. Range: `0-12`. Default: `5`.
