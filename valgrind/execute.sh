valgrind --tool=cachegrind --D1=32768,2,32 --I1=32768,2,32 --LL=65536,2,32 ./valgrind_code.out
cat /content/cachegrind*
rm /content/cachegrind*