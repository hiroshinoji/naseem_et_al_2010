Small modifications to the implementation of an unsupervised parser described in [Naseem et al. (2010) paper](http://www.anthology.aclweb.org/D/D10/D10-1120.pdf).

The original implementation can be found [here](http://groups.csail.mit.edu/rbg/code/dependency/).

The modifications are:
- Support of training and test on different datasets; the original version can only perform both in the same datset. So for example you can train the model on sentences with maximum length 10 and test it on entire test sentences.
- An example rules specific for Universal Dependencies (UD) (`rules_ud` and `map_ud`).
- A script to train and test from conll style files (`train_test_ud.py`).

### Example usage

If you have a CoNLL-formatted treebanks (`train.conll` and `test.conll`), you can train the model and evaluate the performance of it against the test treebank by:

``` shell
$ ./train_test_ud.py train.conll test.conll out
```

where the predicted dependencies for test sentences are outputted in `out`. Note that the format of this file is not CoNLL, but the original one of Naseem et al.

The evaluation score (unlabelled attachment score) can be found at the end of standard output, like this:

``` shell
...
variational bound: -3297.25
round .... 50
Done .....

Evaluating test sentences:
accuracy: 0.292275574113
total: 479
correct: 140
```

