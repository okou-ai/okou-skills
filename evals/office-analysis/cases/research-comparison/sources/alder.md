# Alder: PassageFuse (fictional report)

## 1. Method

PassageFuse encodes each question-passage pair separately; the decoder attends
to all encoded passages together. The reader starts from a pretrained
encoder-decoder and is fine-tuned on answer text. Retrieval is supplied by a
separate system and is not trained with the reader in these experiments.

## 2. Main results

QA-X test exact match, normalized against any reference answer:

| Method | Reader | Retrieval | Passages | EM |
| --- | --- | --- | --- | --- |
| PassageFuse | 240M | dense | 80 | 49.8 |
| QueryMarginal baseline | 410M | dense | 10 | 46.2 |

## 3. Additional comparison

Our approach obtains 42.6 EM with a 240M reader and lexical retrieval. The
closed-book reader obtains 35.0 without the external passage collection. These
are different configurations from the dense-retrieval result in section 2.
No architecture-controlled comparison or production latency test is reported.
