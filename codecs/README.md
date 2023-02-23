# Programs
[FFmpeg](https://ffmpeg.org)

# Container
Use `mkv` (more widely supported) or `nut` (can contain more less used codecs) since they are open formats.

# Video

## Lossy
* If hardware codecs are available, use it. For NVIDIA, use `hevc_nvenc` (have not tested AV1).
* Else, use `libx264` as it is the most optimised (software) codecs in FFmpeg (also being written in x86 assembly).

### Lossless
Same as lossy, but use `libx264rgb` instead of `libx264`. Try to use RGB as RGB to YUV (4:4:4) 8-bit is lossy.
`ffv1` is worse than `libx264rgb`.
* `libx264rgb`: `-qp 0 -preset ultrafast`
* `hevc_nvenc`: `-pix_fmt gbrp -tune lossless` (add `-preset p1` if speed is more prioritised than size)

`apng` might have better compression ratio, but it is very slow.
`huffyuv`/`ffvhuff` is very fast, but have significant size (still better than uncompresed).
