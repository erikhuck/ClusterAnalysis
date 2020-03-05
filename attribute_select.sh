for THRESHOLD in 0.1 0.2
do
    java -cp ~/weka-3-8-4/weka.jar weka.attributeSelection.CorrelationAttributeEval -s "weka.attributeSelection.Ranker -T ${THRESHOLD} -N -1" -i data.arff \
    | python3 attribute_select.py ${THRESHOLD}
done

