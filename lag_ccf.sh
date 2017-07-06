#! /bin/bash

projloca="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
dcf_pos=$projloca"/code/dcf_f90"
all_rmid=$projloca"/result/lightcurve"
rm_res=$projloca"/result/revmap"

cd $rm_res
mkdir "dcf"
cd $all_rmid

for file in ./*
do
    rmid=$file
    echo "Running dcf on $rmid"
    cd $rmid
    cp $dcf_pos .
    chmod +x dcf_f90
    input_arg="2\ndcf\nn\n0\nn\n100\ncont.txt\nhbeta.txt\n"
    printf "$input_arg" | ./dcf_f90
    mv "dcf.dcf" $rm_res"/dcf/"$rmid".txt"
    rm -f "dcf.lc1"
    rm -f "dcf.lc2"
    rm -f "dcf_f90"
    cd $all_rmid
done
