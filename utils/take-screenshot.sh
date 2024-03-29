#!/bin/sh

cmd_pre="ffmpeg -hide_banner -loglevel warning -f x11grab -framerate 1000 -draw_mouse 0"
cmd_post="-i $DISPLAY -frames:v 1 -update 1 -c:v png"
file_path="$HOME/Pictures/Screenshots/Screenshot_$(date '+%Y-%m-%d_%H-%M-%S').png"

case "$1" in
	'fullscreen')
		options=""
		;;
	'window')
		options="-window_id $(xdotool getactivewindow)"
		;;
	'region')
		options="-select_region 1"
		;;
	*)
		echo "Error: Unknown screenshot type: $1 (fullscreen, window, region)"
		exit 1
		;;
esac

case $2 in
	'file')
		output="$file_path"
		result_msg="file: $file_path"
		;;
	'clipboard')
		output="-f image2pipe pipe:1 | xclip -i -t image/png -selection clipboard"
		result_msg="clipboard"
		;;
	*)
		echo "Error: Unknown output type: $2 (file, clipboard)"
		exit 1
		;;
esac

eval $cmd_pre $options $cmd_post $output
echo "Screenshot saved to $result_msg"
notify-send "Screenshot taken" "Screenshot saved to $result_msg"
