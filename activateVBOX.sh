#!/bin/bash

path=~/code/RC-P
for i in {1..9}; do
    
    cd $path/cfg/r$i/ && rm -f *.pcap && numarEth=$(ls -1 | wc -l)
    numarEth=$((numarEth+1))
    for((j=1;j<=numarEth;j++)); do
        VBoxManage modifyvm "R0$i" --nictrace$j on --nictracefile$j $path/cfg/r$i/file$j.pcap
    done
    
done

cd $path/cfg/r10/ && rm -f *.pcap && numarEth=$(ls -1 | wc -l)
numarEth=$((numarEth+1))
for((j=1;j<=numarEth;j++)); do
    VBoxManage modifyvm "R10" --nictrace$j on --nictracefile$j $path/cfg/r10/file$j.pcap
done
