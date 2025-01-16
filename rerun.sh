
path=~/pr
cd path && touch pass.txt && echo "rcp" > pass.txt && su < pass.txt && rm -f pass.txt && export ID=$1 && export INF=16 && python3 main.py && su tc
