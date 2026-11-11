# Birch: QueryMarginal (fictional report)

## 1. Method and training

QueryMarginal uses a pretrained dense retriever and a pretrained 410M
encoder-decoder. In downstream training it updates the query encoder and answer
generator while the document encoder and index remain fixed. The answer
probability marginalizes over alternative passages rather than concatenating
their encoded representations for simultaneous decoder attention.

## 2. Results

The main QA-X test result is 46.2 EM using 10 dense-retrieved passages. This
report lists PassageFuse as 49.1 EM in its comparison table. It does not identify
the exact PassageFuse checkpoint or provide enough information to reconcile
49.1 with Alder's section 2 value. Neither report establishes a typo or a causal
explanation of the difference. This report does not give per-question outputs,
training-compute parity or a matched-latency comparison.
