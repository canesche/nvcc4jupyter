CODE=($1)

for ((i=0; i < ${#CODE[@]}; i++)) do
    grep \"${CODE[i]}\" /content/m5out/stats.txt
done