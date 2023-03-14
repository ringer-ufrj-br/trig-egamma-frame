INPUT=$1
OUTPUT=$2
python prun_hadd.py --nFilesPerMerge 50 -j 40 -o $OUTPUT -i $INPUT