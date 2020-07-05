COHORT="adni"

for THRESHOLD in 0.1 0.2 0.3
do
    java -cp ~/weka-3-8-4/weka.jar weka.attributeSelection.InfoGainAttributeEval -s "weka.attributeSelection.Ranker -T ${THRESHOLD} -N -1" -i clean-data/${COHORT}/data.arff \
    | python3 feat-select/feat-select.py ${THRESHOLD}
done

