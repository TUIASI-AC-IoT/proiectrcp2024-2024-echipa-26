
path=~/code/RC-P
for i in {1..10}; do 

    auxPath=$path/cfg/r$i
    rm -f $auxPath/r$i.pcap
    files=$(find $auxPath -maxdepth 1 -type f -name "*.pcap")
    mergecap -w $auxPath/r$i.pcap $files
done