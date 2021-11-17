#!/bin/sh
input_file="$1"
block_size="$(expr 256 '*' 1024 '*' 1024)"
input_file_size="$(lsblk -n -d -b -o SIZE ${input_file})"
range_size="$(expr ${input_file_size} '/' 127)"
block_count="$(expr ${range_size} '/' ${block_size})"
current_block=0
temp_result_file="$(mktemp --suffix='-benchmark-file-regions.txt')"

if [ -z "${input_file}" ]
then
	printf 'Benchmark the reading speed on multiple regions of the file.\n'
	printf 'Usage: %s <file>\n' "$(basename "$0")"
	exit
fi

finish() {
	echo
	echo 'Stopping...'
	chmod 644 "${temp_result_file}"
	sed -i '/\r/d' "${temp_result_file}"
	printf '\nThe result file is: %s\n' "${temp_result_file}"
	exit
}

trap finish SIGINT
trap finish SIGTERM

printf 'Reading %s (%s bytes)' "${input_file}" "${input_file_size}" | tee -a "${temp_result_file}"
while [ "$(expr ${current_block} '*' ${block_size})" -lt "${input_file_size}" ]
do
	printf '\nCurrently at the %sth block (~%s %s)\n' \
	"${current_block}" \
	"$(expr '(' ${current_block} '*' ${block_size} ')' '/' \
	'(' 1024 '*' 1024 '*' 1024 ')')" \
	'GiB' | tee -a "${temp_result_file}"
	printf 'The block size is: %s\n' "${block_size}" | tee -a "${temp_result_file}"

	dd bs="${block_size}" count="${block_count}" if="${input_file}" \
	iflag=direct skip="${current_block}" of=/dev/null \
	status=progress 2>&1 | tee -a "${temp_result_file}"

	current_block="$(expr ${current_block} '+' ${block_count})"
done

printf '\nDisk benchmark completed.\n' | tee -a "${temp_result_file}"
finish
