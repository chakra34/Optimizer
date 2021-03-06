#!/bin/bash
job="$1"
/opt/soft/MSC/marc2013.1/tools/run_damask -prog /egr/research/CMM/DAMASK/chakra34/code/DAMASK_marc.marc -jid ${job} -q b -ml 387555 -ci no -cr no -ver no
sleep 5
while [ -e ./*.pid ]
do
 sleep 5
 echo waiting
done
#echo " postResults starts"
#~/bin/postResults --cr=f,p model1_job1_solder.t16 
#while [ ! -e ./postProc/model*.txt ]
#do
 #sleep 2
 #echo "postResults going on"
#done 
# ~/bin/addStrainTensors -v -0 ./postProc/*.txt
#echo addStrain
#while ! grep -q "9_ln(V)" ./postProc/*.txt
#do
# echo "adding strain tensors"
# sleep 3
#done
#~/bin/addCauchy ./postProc/*.txt
#echo addCauchy

#while ! grep -q "9_Cauchy" ./postProc/*.txt
#do
# echo "adding Cauchy"
# sleep 3
#done
#~/bin/addMises -e 'ln(V)' -s Cauchy ./postProc/*.txt
#echo addMises
#while ! grep -q "Mises(Cauchy)" ./postProc/*.txt
#do
# echo "adding Mises"
# sleep 3
#done
#~/bin/filterTable --white='Mises(ln(V))','Mises(Cauchy)' < ./postProc/*.txt > marc_result.txt
#echo filter

#rm model*.t16
res=`grep "3004" *.sts | awk '{print \$7}'`
[[ $res -eq 3004 ]] && echo 'N o r m a l' || echo 'E r r o r'
